// Vercel Serverless Function — POST /api/upload
// Simpan SATU file bukti ke GitHub di folder uploads/<divisi>/<namafile>
// Body: { divisi, name, dataUrl }  (dataUrl = "data:<mime>;base64,....")
// Return: { ok:true, url:"https://raw.githubusercontent.com/.../uploads/<divisi>/<file>" }

const REPO   = 'pinuspackindo-ai/pinuspackindo-okr';
const BRANCH = 'data';

function ghHeaders(token) {
  return {
    'Authorization': `token ${token}`,
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json',
    'User-Agent': 'PINUS-OKR-Vercel',
  };
}

function slug(s) {
  return String(s || '').replace(/[^a-zA-Z0-9._-]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 80) || 'file';
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, msg: 'Method not allowed' });
  }
  const TOKEN = process.env.GITHUB_TOKEN || '';
  if (!TOKEN) {
    return res.status(500).json({ ok: false, msg: 'GITHUB_TOKEN belum di-set di Vercel' });
  }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  const divisi = slug(body && body.divisi ? body.divisi : 'umum');
  const dataUrl = (body && body.dataUrl) || '';
  if (!dataUrl || dataUrl.indexOf('base64,') === -1) {
    return res.status(400).json({ ok: false, msg: 'dataUrl tidak valid' });
  }

  // tentukan ekstensi dari mime / nama
  let ext = '';
  const m = dataUrl.match(/^data:([^;]+);base64,/);
  const mime = m ? m[1] : '';
  const nameExt = (String(body.name || '').match(/\.([a-zA-Z0-9]{1,5})$/) || [])[1];
  if (nameExt) ext = '.' + nameExt.toLowerCase();
  else if (mime.indexOf('jpeg') !== -1) ext = '.jpg';
  else if (mime.indexOf('png') !== -1) ext = '.png';
  else if (mime.indexOf('pdf') !== -1) ext = '.pdf';
  else if (mime.indexOf('sheet') !== -1) ext = '.xlsx';
  else ext = '.bin';

  const content = dataUrl.split('base64,')[1];
  const stamp = Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  const baseName = slug((String(body.name || 'bukti').replace(/\.[a-zA-Z0-9]{1,5}$/, ''))) ;
  const path = `uploads/${divisi}/${stamp}_${baseName}${ext}`;
  const API = `https://api.github.com/repos/${REPO}/contents/${encodeURI(path)}`;

  const putBody = {
    message: `chore: upload bukti ${divisi}/${baseName}${ext} [vercel skip]`,
    content,
    branch: BRANCH,
  };

  try {
    const r = await fetch(API, { method: 'PUT', headers: ghHeaders(TOKEN), body: JSON.stringify(putBody) });
    if (!r.ok) {
      const t = await r.text();
      return res.status(500).json({ ok: false, msg: 'GitHub PUT gagal: ' + t.slice(0, 200) });
    }
    const url = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${encodeURI(path)}`;
    return res.status(200).json({ ok: true, url, path });
  } catch (e) {
    return res.status(500).json({ ok: false, msg: String(e) });
  }
};
