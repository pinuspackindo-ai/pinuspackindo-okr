// Penanda tangan AWS SigV4 untuk Backblaze B2 (S3-compatible API).
// Ditulis manual dengan modul crypto bawaan Node supaya proyek ini tetap
// tanpa dependency (tidak ada package.json / node_modules di Vercel).
//
// ENV yang dipakai:
//   B2_KEY_ID    — Application Key ID dari Backblaze
//   B2_APP_KEY   — Application Key (rahasia)
//   B2_BUCKET    — nama bucket, mis. pinuspackindo-okr
//   B2_ENDPOINT  — host endpoint, mis. s3.us-east-005.backblazeb2.com
//   B2_REGION    — opsional; kalau kosong diambil dari endpoint (us-east-005)

const crypto = require('crypto');

function cfg() {
  const endpoint = (process.env.B2_ENDPOINT || '').replace(/^https?:\/\//, '').replace(/\/+$/, '');
  const m = endpoint.match(/^s3\.([a-z0-9-]+)\.backblazeb2\.com$/i);
  return {
    keyId: process.env.B2_KEY_ID || '',
    appKey: process.env.B2_APP_KEY || '',
    bucket: process.env.B2_BUCKET || '',
    endpoint,
    region: process.env.B2_REGION || (m ? m[1] : 'us-east-005'),
  };
}

function siap() {
  const c = cfg();
  return !!(c.keyId && c.appKey && c.bucket && c.endpoint);
}

const sha256 = (b) => crypto.createHash('sha256').update(b).digest('hex');
const hmac = (key, data) => crypto.createHmac('sha256', key).update(data).digest();

// Setiap segmen path di-encode, tapi "/" pemisah tetap utuh
function encodeKey(key) {
  return String(key).split('/').map(encodeURIComponent).join('/');
}

function stamps() {
  const iso = new Date().toISOString().replace(/[:-]|\.\d{3}/g, ''); // 20260811T050000Z
  return { amzDate: iso, dateOnly: iso.slice(0, 8) };
}

function signingKey(appKey, dateOnly, region) {
  let k = hmac('AWS4' + appKey, dateOnly);
  k = hmac(k, region);
  k = hmac(k, 's3');
  return hmac(k, 'aws4_request');
}

/**
 * Tanda tangani satu permintaan ke B2 lalu kembalikan { url, headers } siap dipakai fetch().
 * @param {string} method   GET | PUT | DELETE | HEAD
 * @param {string} key      path objek di dalam bucket, mis. uploads/purchasing/abc.xlsx
 * @param {Buffer|string} body  isi untuk PUT (kosongkan utk GET)
 * @param {string} contentType  opsional, hanya utk PUT
 */
function signRequest(method, key, body, contentType) {
  const c = cfg();
  if (!siap()) throw new Error('ENV Backblaze belum lengkap (B2_KEY_ID/B2_APP_KEY/B2_BUCKET/B2_ENDPOINT)');

  const payload = body === undefined || body === null ? '' : body;
  const payloadHash = sha256(payload);
  const { amzDate, dateOnly } = stamps();
  const canonicalUri = '/' + c.bucket + '/' + encodeKey(key);

  // Header yang ikut ditandatangani — urut abjad, wajib termasuk host
  const signed = [
    ['host', c.endpoint],
    ['x-amz-content-sha256', payloadHash],
    ['x-amz-date', amzDate],
  ];
  const canonicalHeaders = signed.map(([k, v]) => k + ':' + v + '\n').join('');
  const signedHeaders = signed.map(([k]) => k).join(';');

  const canonicalRequest = [method, canonicalUri, '', canonicalHeaders, signedHeaders, payloadHash].join('\n');
  const scope = [dateOnly, c.region, 's3', 'aws4_request'].join('/');
  const toSign = ['AWS4-HMAC-SHA256', amzDate, scope, sha256(canonicalRequest)].join('\n');
  const signature = crypto.createHmac('sha256', signingKey(c.appKey, dateOnly, c.region)).update(toSign).digest('hex');

  // CATATAN: 'host' ikut ditandatangani (wajib), tapi TIDAK dikirim sebagai header
  // manual — fetch bawaan Node (undici) mengisi Host sendiri dari URL, dan menolak
  // kalau kita set ulang. Nilainya sama, jadi tanda tangan tetap sah.
  const headers = {
    'x-amz-content-sha256': payloadHash,
    'x-amz-date': amzDate,
    'Authorization': `AWS4-HMAC-SHA256 Credential=${c.keyId}/${scope}, SignedHeaders=${signedHeaders}, Signature=${signature}`,
  };
  if (contentType) headers['Content-Type'] = contentType;

  return { url: `https://${c.endpoint}${canonicalUri}`, headers };
}

/** Simpan objek ke bucket. Melempar Error kalau B2 menolak. */
async function putObject(key, buf, contentType) {
  const { url, headers } = signRequest('PUT', key, buf, contentType);
  const r = await fetch(url, { method: 'PUT', headers, body: buf });
  if (!r.ok) throw new Error('B2 PUT ' + r.status + ': ' + (await r.text()).slice(0, 200));
  return key;
}

/** Ambil objek dari bucket. Kembalikan Response apa adanya (dipakai utk proxy). */
async function getObject(key) {
  const { url, headers } = signRequest('GET', key);
  return fetch(url, { method: 'GET', headers });
}

module.exports = { cfg, siap, putObject, getObject, signRequest, encodeKey };
