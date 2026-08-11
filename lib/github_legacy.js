// Jalur LAMA (GitHub) — dipakai hanya selama masa migrasi, sebagai cadangan
// kalau ENV Supabase / Backblaze belum diisi. Setelah migrasi selesai dan repo
// GitHub dihapus, file ini beserta pemanggilnya bisa dibuang.

const REPO = 'pinuspackindo-ai/pinuspackindo-okr';
const BRANCH = 'data';
const FILE = 'okr_data.json';
const API = `https://api.github.com/repos/${REPO}/contents/${FILE}`;

function siap() {
  return !!process.env.GITHUB_TOKEN;
}

function headers(token) {
  return {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json',
    'User-Agent': 'PINUS-OKR-Vercel',
  };
}

async function handleOkr(req, res) {
  const TOKEN = process.env.GITHUB_TOKEN || '';

  if (req.method === 'GET') {
    try {
      const r = await fetch(`${API}?ref=${BRANCH}`, {
        headers: { 'Authorization': `token ${TOKEN}`, 'Accept': 'application/vnd.github.raw', 'User-Agent': 'PINUS-OKR-Vercel' },
      });
      if (r.ok) {
        const teks = await r.text();
        const d = JSON.parse(teks);
        return res.status(200).json(req.query && req.query.meta ? { _ts: d._ts || 0 } : d);
      }
    } catch (e) { /* lanjut ke raw */ }
    try {
      const r = await fetch(`https://raw.githubusercontent.com/${REPO}/${BRANCH}/${FILE}?_=${Date.now()}`);
      if (r.ok) {
        const d = JSON.parse(await r.text());
        return res.status(200).json(req.query && req.query.meta ? { _ts: d._ts || 0 } : d);
      }
    } catch (e) { /* menyerah */ }
    return res.status(200).json({});
  }

  if (req.method === 'POST') {
    let data = req.body;
    if (typeof data === 'string') { try { data = JSON.parse(data); } catch (e) { data = null; } }
    if (!data || typeof data !== 'object') return res.status(400).json({ ok: false, msg: 'Data tidak valid' });

    const _json = JSON.stringify(data, null, 2);
    if (_json.indexOf('"__CLOUD__"') !== -1) {
      return res.status(200).json({ ok: false, skipped: true, msg: 'Ditolak: data mengandung placeholder __CLOUD__ (file belum termuat).' });
    }
    let sha = '';
    try {
      const r = await fetch(`${API}?ref=${BRANCH}`, { headers: headers(TOKEN) });
      if (r.ok) sha = (await r.json()).sha || '';
    } catch (e) { /* file baru */ }
    try {
      const r = await fetch(API, {
        method: 'PUT',
        headers: headers(TOKEN),
        body: JSON.stringify({
          message: 'chore: update OKR data [vercel skip]',
          content: Buffer.from(_json, 'utf8').toString('base64'),
          branch: BRANCH,
          ...(sha ? { sha } : {}),
        }),
      });
      return res.status(r.ok ? 200 : 500).json({ ok: r.ok, legacy: 'github' });
    } catch (e) {
      return res.status(500).json({ ok: false, msg: String(e) });
    }
  }

  return res.status(405).json({ ok: false, msg: 'Method not allowed' });
}

/** Upload satu file ke GitHub (jalur lama). Kembalikan {url, path}. */
async function uploadFile(key, buf) {
  const TOKEN = process.env.GITHUB_TOKEN || '';
  const url = `https://api.github.com/repos/${REPO}/contents/${encodeURI(key)}`;
  const r = await fetch(url, {
    method: 'PUT',
    headers: headers(TOKEN),
    body: JSON.stringify({ message: `chore: upload ${key} [vercel skip]`, content: buf.toString('base64'), branch: BRANCH }),
  });
  if (!r.ok) throw new Error('GitHub PUT gagal: ' + (await r.text()).slice(0, 200));
  return { url: `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${encodeURI(key)}`, path: key };
}

module.exports = { siap, handleOkr, uploadFile, REPO, BRANCH, FILE };
