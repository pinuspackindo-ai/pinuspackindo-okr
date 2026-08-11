// Vercel Serverless Function — POST /api/upload
// Simpan SATU file bukti ke bucket Backblaze B2: uploads/<divisi>/<stamp>_<nama>
// Body: { divisi, name, dataUrl }   (dataUrl = "data:<mime>;base64,....")
// Return: { ok:true, url:"https://<host>/api/file?k=uploads/...", key }
//
// Bucket B2 bersifat PRIVATE, jadi yang disimpan di data OKR bukan URL B2
// langsung (butuh tanda tangan & kedaluwarsa), melainkan URL /api/file milik
// aplikasi sendiri yang mem-proxy isinya. URL-nya absolut supaya semua kode
// frontend yang menguji /^https?:/ tetap bekerja tanpa diubah.

const b2 = require('../lib/s3sign');
const gh = require('../lib/github_legacy');

function slug(s) {
  return String(s || '').replace(/[^a-zA-Z0-9._-]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 80) || 'file';
}

function extDari(mime, name) {
  const nameExt = (String(name || '').match(/\.([a-zA-Z0-9]{1,5})$/) || [])[1];
  if (nameExt) return '.' + nameExt.toLowerCase();
  if (mime.indexOf('jpeg') !== -1) return '.jpg';
  if (mime.indexOf('png') !== -1) return '.png';
  if (mime.indexOf('pdf') !== -1) return '.pdf';
  if (mime.indexOf('sheet') !== -1) return '.xlsx';
  return '.bin';
}

function asalPermintaan(req) {
  const proto = (req.headers['x-forwarded-proto'] || 'https').split(',')[0];
  const host = req.headers['x-forwarded-host'] || req.headers.host || '';
  return proto + '://' + host;
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, msg: 'Method not allowed' });
  }
  // DWI-MODE: B2 kalau ENV-nya sudah ada, kalau belum jatuh ke GitHub (jalur lama)
  const pakaiB2 = b2.siap();
  if (!pakaiB2 && !gh.siap()) {
    return res.status(500).json({ ok: false, msg: 'ENV Backblaze belum di-set di Vercel (B2_KEY_ID, B2_APP_KEY, B2_BUCKET, B2_ENDPOINT)' });
  }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  const dataUrl = (body && body.dataUrl) || '';
  if (!dataUrl || dataUrl.indexOf('base64,') === -1) {
    return res.status(400).json({ ok: false, msg: 'dataUrl tidak valid' });
  }

  const divisi = slug(body && body.divisi ? body.divisi : 'umum');
  const m = dataUrl.match(/^data:([^;]+);base64,/);
  const mime = m ? m[1] : 'application/octet-stream';
  const ext = extDari(mime, body.name);
  const baseName = slug(String(body.name || 'bukti').replace(/\.[a-zA-Z0-9]{1,5}$/, ''));
  const stamp = Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  const key = `uploads/${divisi}/${stamp}_${baseName}${ext}`;

  try {
    const buf = Buffer.from(dataUrl.split('base64,')[1], 'base64');
    if (!pakaiB2) {
      const hasil = await gh.uploadFile(key, buf);
      return res.status(200).json({ ok: true, url: hasil.url, key, path: key, size: buf.length, legacy: 'github' });
    }
    await b2.putObject(key, buf, mime);
    // URL RELATIF, bukan absolut: file yang sama jadi bisa dibuka dari dashboard
    // lokal (Flask) maupun versi web tanpa perlu menulis ulang data.
    const url = '/api/file?k=' + key;
    return res.status(200).json({ ok: true, url, key, path: key, size: buf.length });
  } catch (e) {
    return res.status(500).json({ ok: false, msg: String(e).slice(0, 300) });
  }
};
