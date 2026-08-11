// Vercel Serverless Function — GET /api/migrate?token=...&step=...
// Migrasi SEKALI JALAN dari GitHub → Supabase (data) + Backblaze B2 (file).
//
// Dijalankan di server supaya kredensial tidak pernah keluar dari Vercel.
// Semua langkah AMAN DIULANG (idempoten): yang sudah dipindah akan dilewati.
//
//   step=status  → laporan: sumber data, jumlah file yang belum dipindah
//   step=data    → salin okr_data.json dari GitHub ke Supabase (tidak menimpa
//                  kalau Supabase sudah berisi data, kecuali &force=1)
//   step=files   → pindahkan file batch berikutnya ke B2 lalu tulis ulang URL-nya
//                  di data OKR. Ulangi sampai "sisa" = 0. &limit=<n> (default 20)
//
// ENV tambahan: MIGRATE_TOKEN — token bebas buatan sendiri, wajib cocok.

const supa = require('../lib/supa');
const b2 = require('../lib/s3sign');

const GH_REPO = 'pinuspackindo-ai/pinuspackindo-okr';
const RAW_RE = /https:\/\/raw\.githubusercontent\.com\/[^"'\s\\]+/g;
const BATAS_MS = 45000; // sisakan waktu sebelum batas eksekusi Vercel

function asalPermintaan(req) {
  const proto = (req.headers['x-forwarded-proto'] || 'https').split(',')[0];
  const host = req.headers['x-forwarded-host'] || req.headers.host || '';
  return proto + '://' + host;
}

// Kumpulkan semua URL raw.githubusercontent yang masih ada di dalam data
function kumpulkanUrl(data) {
  const s = JSON.stringify(data || {});
  const semua = s.match(RAW_RE) || [];
  return [...new Set(semua)];
}

// uploads/<divisi>/<file> diambil dari URL GitHub; kalau tidak ada pola uploads/
// (mis. file lama di root) dipetakan ke uploads/umum/<file>
function keyDariUrl(u) {
  const m = decodeURIComponent(u).match(/\/uploads\/([^\/]+)\/([^\/?#]+)$/);
  if (m) return `uploads/${m[1]}/${m[2]}`;
  const nama = decodeURIComponent(u).split('/').pop().split('?')[0];
  return `uploads/umum/${nama}`;
}

function ganti(data, dari, ke) {
  const s = JSON.stringify(data);
  // ganti semua kemunculan, termasuk yang muncul di beberapa tempat
  return JSON.parse(s.split(JSON.stringify(dari).slice(1, -1)).join(JSON.stringify(ke).slice(1, -1)));
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');

  const TOKEN = process.env.MIGRATE_TOKEN || '';
  if (!TOKEN) return res.status(500).json({ ok: false, msg: 'MIGRATE_TOKEN belum di-set di Vercel' });
  if (!req.query || req.query.token !== TOKEN) return res.status(403).json({ ok: false, msg: 'Token salah' });

  const step = String((req.query && req.query.step) || 'status');
  const siap = { supabase: supa.siap(), b2: b2.siap(), github: !!process.env.GITHUB_TOKEN };

  try {
    // ── STATUS ────────────────────────────────────────────────
    if (step === 'status') {
      let data = {};
      try { data = await supa.getState(); } catch (e) { /* biarkan kosong */ }
      const urls = kumpulkanUrl(data);
      return res.status(200).json({
        ok: true, siap,
        supabase: { adaBaris: Object.keys(data).length > 0, jumlahKunci: Object.keys(data).length, _ts: data._ts || null },
        fileBelumDipindah: urls.length,
        contoh: urls.slice(0, 3),
      });
    }

    // ── DATA: GitHub → Supabase ───────────────────────────────
    if (step === 'data') {
      if (!siap.supabase) return res.status(500).json({ ok: false, msg: 'ENV Supabase belum lengkap' });
      const lama = await supa.getState();
      if (Object.keys(lama).length && req.query.force !== '1') {
        return res.status(200).json({ ok: false, msg: 'Supabase sudah berisi data (' + Object.keys(lama).length + ' kunci). Tambahkan &force=1 kalau memang ingin ditimpa.' });
      }
      const url = `https://raw.githubusercontent.com/${GH_REPO}/data/okr_data.json?_=${Date.now()}`;
      const r = await fetch(url);
      if (!r.ok) return res.status(502).json({ ok: false, msg: 'Gagal baca okr_data.json dari GitHub: ' + r.status });
      const teks = await r.text();
      let data;
      try { data = JSON.parse(teks); } catch (e) { return res.status(502).json({ ok: false, msg: 'okr_data.json tidak bisa di-parse' }); }
      if (teks.indexOf('"__CLOUD__"') !== -1) {
        return res.status(400).json({ ok: false, msg: 'Ditolak: sumber mengandung placeholder __CLOUD__' });
      }
      await supa.putState(data);
      return res.status(200).json({ ok: true, dipindah: 'okr_data.json', jumlahKunci: Object.keys(data).length, ukuranKB: Math.round(teks.length / 1024), fileMenungguDipindah: kumpulkanUrl(data).length });
    }

    // ── FILES: GitHub → B2, lalu tulis ulang URL di data ──────
    if (step === 'files') {
      if (!siap.supabase) return res.status(500).json({ ok: false, msg: 'ENV Supabase belum lengkap' });
      if (!siap.b2) return res.status(500).json({ ok: false, msg: 'ENV Backblaze belum lengkap' });

      const limit = Math.max(1, Math.min(50, parseInt(req.query.limit || '20', 10)));
      let data = await supa.getState();
      const urls = kumpulkanUrl(data);
      if (!urls.length) return res.status(200).json({ ok: true, selesai: true, sisa: 0, msg: 'Tidak ada file GitHub yang tersisa di data.' });

      const asal = asalPermintaan(req);
      const mulai = Date.now();
      const berhasil = [], gagal = [];

      for (const u of urls.slice(0, limit)) {
        if (Date.now() - mulai > BATAS_MS) break;
        try {
          const rr = await fetch(u);
          if (!rr.ok) { gagal.push({ url: u, sebab: 'GitHub ' + rr.status }); continue; }
          const buf = Buffer.from(await rr.arrayBuffer());
          const key = keyDariUrl(u);
          await b2.putObject(key, buf, rr.headers.get('content-type') || 'application/octet-stream');
          data = ganti(data, u, asal + '/api/file?k=' + encodeURIComponent(key));
          berhasil.push({ key, byte: buf.length });
        } catch (e) {
          gagal.push({ url: u, sebab: String(e).slice(0, 120) });
        }
      }

      if (berhasil.length) {
        data._ts = Date.now();
        await supa.putState(data);
      }
      const sisa = kumpulkanUrl(data).length;
      return res.status(200).json({
        ok: true, selesai: sisa === 0, dipindah: berhasil.length, sisa,
        totalByte: berhasil.reduce((a, b) => a + b.byte, 0),
        gagal, contohBerhasil: berhasil.slice(0, 3),
      });
    }

    return res.status(400).json({ ok: false, msg: 'step tidak dikenal. Pakai status | data | files' });
  } catch (e) {
    return res.status(500).json({ ok: false, msg: String(e).slice(0, 400) });
  }
};
