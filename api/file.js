// Vercel Serverless Function — GET /api/file?k=uploads/<divisi>/<namafile>
// Mem-proxy isi objek dari bucket Backblaze B2 yang PRIVATE.
//
// Kenapa proxy, bukan presigned URL yang di-redirect:
//   - selalu satu origin dengan aplikasi → tidak perlu mengatur CORS di bucket,
//     padahal frontend membaca .xlsx lewat fetch() yang tunduk CORS;
//   - tidak ada URL bertanda tangan yang bocor / kedaluwarsa di data OKR.

const b2 = require('../lib/s3sign');

const MIME = {
  jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', gif: 'image/gif', webp: 'image/webp',
  pdf: 'application/pdf',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  xls: 'application/vnd.ms-excel', csv: 'text/csv', txt: 'text/plain',
};

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return res.status(405).json({ ok: false, msg: 'Method not allowed' });
  }
  if (!b2.siap()) {
    return res.status(500).json({ ok: false, msg: 'ENV Backblaze belum di-set di Vercel' });
  }

  const key = String((req.query && req.query.k) || '');
  // Hanya izinkan objek di dalam uploads/ dan tolak upaya keluar folder
  if (!key || key.indexOf('..') !== -1 || !/^uploads\/[A-Za-z0-9._\-]+\/[A-Za-z0-9._\-]+$/.test(key)) {
    return res.status(400).json({ ok: false, msg: 'Parameter k tidak valid' });
  }

  try {
    const r = await b2.getObject(key);
    if (!r.ok) {
      return res.status(r.status === 404 ? 404 : 502).json({ ok: false, msg: 'B2 GET ' + r.status });
    }
    const ext = (key.match(/\.([A-Za-z0-9]{1,5})$/) || [])[1];
    const ct = r.headers.get('content-type');
    res.setHeader('Content-Type', (ext && MIME[ext.toLowerCase()]) || ct || 'application/octet-stream');
    res.setHeader('Cache-Control', 'private, max-age=300');
    const nama = key.split('/').pop();
    res.setHeader('Content-Disposition', 'inline; filename="' + nama.replace(/"/g, '') + '"');
    if (req.method === 'HEAD') return res.status(200).end();
    const buf = Buffer.from(await r.arrayBuffer());
    return res.status(200).send(buf);
  } catch (e) {
    return res.status(500).json({ ok: false, msg: String(e).slice(0, 300) });
  }
};
