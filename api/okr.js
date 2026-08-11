// Vercel Serverless Function — GET & POST /api/okr
// GET  → baca seluruh data OKR dari Supabase (tabel okr_state, baris 'main')
// POST → simpan seluruh data OKR ke Supabase
//
// Menggantikan penyimpanan lama di GitHub (okr_data.json pada branch `data`).
// Kontrak ke frontend TIDAK berubah: GET mengembalikan objek okrData apa adanya,
// GET ?meta=1 hanya {_ts}, POST menerima objek penuh.

const supa = require('../lib/supa');
const gh = require('../lib/github_legacy');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');

  // DWI-MODE selama masa migrasi: pakai Supabase kalau ENV-nya sudah ada,
  // kalau belum jatuh ke GitHub (perilaku lama) supaya tidak ada downtime.
  // Setelah migrasi selesai & GitHub dihapus, cabang legacy ini bisa dibuang.
  if (!supa.siap()) {
    if (!gh.siap()) {
      return res.status(500).json({ ok: false, msg: 'Belum ada penyimpanan aktif: set SUPABASE_URL + SUPABASE_SERVICE_KEY (atau GITHUB_TOKEN utk mode lama) di Vercel Environment Variables' });
    }
    return gh.handleOkr(req, res);
  }

  // ── GET ─────────────────────────────────────────────────────
  if (req.method === 'GET') {
    try {
      if (req.query && req.query.meta) {
        return res.status(200).json({ _ts: await supa.getTs() });
      }
      const data = await supa.getState();
      res.setHeader('Cache-Control', 'no-store');
      return res.status(200).json(data);
    } catch (e) {
      if (req.query && req.query.dbg) return res.status(200).json({ _debug: String(e) });
      return res.status(200).json({});
    }
  }

  // ── POST ────────────────────────────────────────────────────
  if (req.method === 'POST') {
    let data = req.body;
    if (typeof data === 'string') { try { data = JSON.parse(data); } catch (e) { data = null; } }
    if (!data || typeof data !== 'object') {
      return res.status(400).json({ ok: false, msg: 'Data tidak valid' });
    }

    // GUARD ANTI-CORRUPTION (dipertahankan dari versi GitHub):
    // '__CLOUD__' = isi file belum dipulihkan dari cloud; menyimpannya akan
    // menimpa referensi file asli dengan placeholder.
    if (JSON.stringify(data).indexOf('"__CLOUD__"') !== -1) {
      return res.status(200).json({ ok: false, skipped: true, msg: 'Ditolak: data mengandung placeholder __CLOUD__ (file belum termuat).' });
    }

    try {
      await supa.putState(data);
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ ok: false, msg: String(e).slice(0, 300) });
    }
  }

  return res.status(405).json({ ok: false, msg: 'Method not allowed' });
};
