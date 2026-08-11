"""Akses Backblaze B2 (S3-compatible) dari Python — hanya modul bawaan.

Tidak butuh boto3 / requests, jadi bisa jalan di Python mana pun tanpa install.
Algoritma tanda tangannya AWS SigV4, sama dengan lib/s3sign.js (versi Vercel),
dan sudah diuji terhadap test vector resmi AWS.

Kredensial dibaca dari local_config.py:
    B2_KEY_ID   = '...'
    B2_APP_KEY  = '...'
    B2_BUCKET   = 'pinuspackindo-okr'
    B2_ENDPOINT = 's3.us-east-005.backblazeb2.com'
"""

import hashlib
import hmac
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

B2_KEY_ID = ''
B2_APP_KEY = ''
B2_BUCKET = 'pinuspackindo-okr'
B2_ENDPOINT = 's3.us-east-005.backblazeb2.com'

for _nama in ('B2_KEY_ID', 'B2_APP_KEY', 'B2_BUCKET', 'B2_ENDPOINT'):
    try:
        _nilai = getattr(__import__('local_config'), _nama, '')
        if _nilai:
            globals()[_nama] = _nilai
    except ImportError:
        pass


def siap():
    return bool(B2_KEY_ID and B2_APP_KEY and B2_BUCKET and B2_ENDPOINT)


def _region():
    m = re.match(r'^s3\.([a-z0-9-]+)\.backblazeb2\.com$', B2_ENDPOINT, re.I)
    return m.group(1) if m else 'us-east-005'


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _hmac(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def _signing_key(date_only: str) -> bytes:
    k = _hmac(('AWS4' + B2_APP_KEY).encode(), date_only)
    k = _hmac(k, _region())
    k = _hmac(k, 's3')
    return _hmac(k, 'aws4_request')


def _encode_key(key: str) -> str:
    # tiap segmen di-encode, "/" pemisah tetap utuh
    return '/'.join(urllib.parse.quote(s, safe='') for s in key.split('/'))


def _request(method: str, key: str, body: bytes = b'', content_type: str = ''):
    """Bangun urllib.Request yang sudah ditandatangani."""
    if not siap():
        raise RuntimeError('Kredensial B2 belum lengkap di local_config.py '
                           '(B2_KEY_ID, B2_APP_KEY, B2_BUCKET, B2_ENDPOINT)')
    now = datetime.now(timezone.utc)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_only = amz_date[:8]
    payload_hash = _sha256(body)
    canonical_uri = '/' + B2_BUCKET + '/' + _encode_key(key)

    signed = [
        ('host', B2_ENDPOINT),
        ('x-amz-content-sha256', payload_hash),
        ('x-amz-date', amz_date),
    ]
    canonical_headers = ''.join(f'{k}:{v}\n' for k, v in signed)
    signed_headers = ';'.join(k for k, _ in signed)
    canonical_request = '\n'.join(
        [method, canonical_uri, '', canonical_headers, signed_headers, payload_hash])
    scope = '/'.join([date_only, _region(), 's3', 'aws4_request'])
    to_sign = '\n'.join(['AWS4-HMAC-SHA256', amz_date, scope,
                         _sha256(canonical_request.encode())])
    signature = hmac.new(_signing_key(date_only), to_sign.encode(),
                         hashlib.sha256).hexdigest()

    headers = {
        'x-amz-content-sha256': payload_hash,
        'x-amz-date': amz_date,
        'Authorization': (f'AWS4-HMAC-SHA256 Credential={B2_KEY_ID}/{scope}, '
                          f'SignedHeaders={signed_headers}, Signature={signature}'),
    }
    if content_type:
        headers['Content-Type'] = content_type

    url = f'https://{B2_ENDPOINT}{canonical_uri}'
    return urllib.request.Request(url, data=body if method == 'PUT' else None,
                                  headers=headers, method=method)


def put_object(key: str, data: bytes, content_type: str = 'application/octet-stream') -> str:
    """Simpan objek ke bucket. Melempar RuntimeError kalau B2 menolak."""
    req = _request('PUT', key, data, content_type)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp.read()
            return key
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'B2 PUT {e.code}: {e.read().decode(errors="replace")[:300]}')


def get_object(key: str):
    """Ambil objek. Kembalikan (bytes, content_type)."""
    req = _request('GET', key)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read(), resp.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'B2 GET {e.code}: {e.read().decode(errors="replace")[:200]}')


def list_objects(prefix: str = 'uploads/', max_keys: int = 1000):
    """Daftar key di bucket (untuk verifikasi). Kembalikan list of str."""
    q = urllib.parse.urlencode({'list-type': '2', 'prefix': prefix, 'max-keys': max_keys})
    # ListObjectsV2 memakai query string, jadi ditandatangani terpisah dari _request
    if not siap():
        raise RuntimeError('Kredensial B2 belum lengkap')
    now = datetime.now(timezone.utc)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_only = amz_date[:8]
    payload_hash = _sha256(b'')
    canonical_uri = '/' + B2_BUCKET
    canonical_query = '&'.join(sorted(q.split('&')))
    signed = [('host', B2_ENDPOINT), ('x-amz-content-sha256', payload_hash),
              ('x-amz-date', amz_date)]
    canonical_headers = ''.join(f'{k}:{v}\n' for k, v in signed)
    signed_headers = ';'.join(k for k, _ in signed)
    canonical_request = '\n'.join(['GET', canonical_uri, canonical_query,
                                   canonical_headers, signed_headers, payload_hash])
    scope = '/'.join([date_only, _region(), 's3', 'aws4_request'])
    to_sign = '\n'.join(['AWS4-HMAC-SHA256', amz_date, scope,
                         _sha256(canonical_request.encode())])
    signature = hmac.new(_signing_key(date_only), to_sign.encode(),
                         hashlib.sha256).hexdigest()
    headers = {
        'x-amz-content-sha256': payload_hash,
        'x-amz-date': amz_date,
        'Authorization': (f'AWS4-HMAC-SHA256 Credential={B2_KEY_ID}/{scope}, '
                          f'SignedHeaders={signed_headers}, Signature={signature}'),
    }
    url = f'https://{B2_ENDPOINT}{canonical_uri}?{canonical_query}'
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            xml = resp.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'B2 LIST {e.code}: {e.read().decode(errors="replace")[:200]}')
    return re.findall(r'<Key>([^<]+)</Key>', xml)
