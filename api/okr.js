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
    // Coba via Contents API (butuh token) → fallback ke raw URL (publik, tanpa token)
    if (TOKEN) {
      try {
        const r = await fetch(`${API}?ref=${BRANCH}`, { headers: ghHeaders(TOKEN) });
        if (r.ok) {
          const info = await r.json();
          const raw  = Buffer.from(info.content.replace(/\n/g, ''), 'base64').toString('utf8');
          return res.status(200).json(JSON.parse(raw));
        }
      } catch (e) {}
    }
    // Fallback: baca dari raw URL (repo publik — tidak butuh token)
    try {
      const rawUrl = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${FILE}?_=${Date.now()}`;
      const r = await fetch(rawUrl);
      if (r.ok) {
        const text = await r.text();
        return res.status(200).json(JSON.parse(text));
      }
    } catch (e) {}
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
