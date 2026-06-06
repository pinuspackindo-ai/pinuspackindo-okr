// Vercel Serverless Function — GET & POST /api/okr
// GET  → baca okr_data.json dari GitHub (selalu fresh)
// POST → simpan okr_data.json ke GitHub (tanpa redeploy Vercel)

const REPO   = 'pinuspackindo-ai/pinuspackindo-okr';
const BRANCH = 'data';
const FILE   = 'okr_data.json';
const API    = `https://api.github.com/repos/${REPO}/contents/${FILE}`;

function ghHeaders(token) {
  return {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json',
    'User-Agent': 'PINUS-OKR-Vercel',
  };
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');

  const TOKEN = process.env.GITHUB_TOKEN || '';

  // ── GET: baca data dari GitHub ──────────────────────────────
  if (req.method === 'GET') {
    const dbg = { branch: BRANCH, token: !!TOKEN };
    // Ambil konten LANGSUNG via Contents API + Accept raw (andal utk file besar >1MB)
    if (TOKEN) {
      try {
        const r = await fetch(`${API}?ref=${BRANCH}`, {
          headers: { 'Authorization': `token ${TOKEN}`, 'Accept': 'application/vnd.github.raw', 'User-Agent': 'PINUS-OKR-Vercel' }
        });
        dbg.contents_status = r.status;
        if (r.ok) {
          const text = await r.text();
          dbg.contents_len = text.length;
          try { return res.status(200).json(JSON.parse(text)); }
          catch (pe) { dbg.parse_err = String(pe).slice(0, 120); }
        }
      } catch (e) { dbg.contents_err = String(e).slice(0, 120); }
    }
    // Fallback: raw URL
    try {
      const rawUrl = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${FILE}?_=${Date.now()}`;
      const r = await fetch(rawUrl);
      dbg.raw_status = r.status;
      if (r.ok) {
        const text = await r.text();
        dbg.raw_len = text.length;
        try { return res.status(200).json(JSON.parse(text)); }
        catch (pe2) { dbg.raw_parse_err = String(pe2).slice(0, 120); }
      }
    } catch (e) { dbg.raw_err = String(e).slice(0, 120); }
    if (req.query && req.query.dbg) return res.status(200).json({ _debug: dbg });
    return res.status(200).json({});
  }

  // ── POST: simpan data ke GitHub ─────────────────────────────
  if (req.method === 'POST') {
    if (!TOKEN) {
      return res.status(500).json({ ok: false, msg: 'GITHUB_TOKEN belum di-set di Vercel Environment Variables' });
    }
    const data = req.body;
    if (!data || typeof data !== 'object') {
      return res.status(400).json({ ok: false, msg: 'Data tidak valid' });
    }

    const _json = JSON.stringify(data, null, 2);
    // GUARD ANTI-CORRUPTION: tolak data yang mengandung placeholder '__CLOUD__'.
    // Placeholder = isi file belum dipulihkan dari cloud; menyimpannya akan menimpa file asli.
    if (_json.indexOf('"__CLOUD__"') !== -1) {
      return res.status(200).json({ ok: false, skipped: true, msg: 'Ditolak: data mengandung placeholder __CLOUD__ (file belum termuat).' });
    }

    const content = Buffer.from(_json, 'utf8').toString('base64');

    // Ambil SHA file saat ini (wajib untuk update)
    let sha = '';
    try {
      const r = await fetch(`${API}?ref=${BRANCH}`, { headers: ghHeaders(TOKEN) });
      if (r.ok) sha = (await r.json()).sha || '';
    } catch (e) {}

    // Push ke GitHub — [vercel skip] mencegah Vercel redeploy
    const body = {
      message: 'chore: update OKR data [vercel skip]',
      content,
      branch: BRANCH,
      ...(sha ? { sha } : {}),
    };

    try {
      const r = await fetch(API, {
        method: 'PUT',
        headers: ghHeaders(TOKEN),
        body: JSON.stringify(body),
      });
      return res.status(r.ok ? 200 : 500).json({ ok: r.ok });
    } catch (e) {
      return res.status(500).json({ ok: false, msg: String(e) });
    }
  }

  res.status(405).json({ ok: false, msg: 'Method not allowed' });
};
