"""Migrasi data OKR ke Supabase dan seluruh file ke Backblaze B2.

Dijalankan dari laptop, TIDAK butuh Vercel dan TIDAK butuh install apa pun
(hanya modul bawaan Python).

    py migrasi_ke_cloud.py --cek           # periksa kesiapan & hitung pekerjaan
    py migrasi_ke_cloud.py --data          # pindahkan data OKR ke Supabase
    py migrasi_ke_cloud.py --file          # pindahkan semua file ke B2
    py migrasi_ke_cloud.py --file --limit 20   # coba sedikit dulu

Aman diulang: file yang sudah pindah dilewati. Kalau terputus di tengah,
jalankan lagi perintah yang sama — kemajuan sudah tersimpan di Supabase.

Isi dulu local_config.py (lihat local_config.example.py).
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import b2py

SUPABASE_URL = ''
SUPABASE_SERVICE_KEY = ''
for _n in ('SUPABASE_URL', 'SUPABASE_SERVICE_KEY'):
    try:
        _v = getattr(__import__('local_config'), _n, '')
        if _v:
            globals()[_n] = _v
    except ImportError:
        pass

GH_RAW_DATA = 'https://raw.githubusercontent.com/pinuspackindo-ai/pinuspackindo-okr/data/okr_data.json'
RAW_RE = re.compile(r'https://raw\.githubusercontent\.com/[^"\'\s\\]+')
SIMPAN_TIAP = 10  # simpan kemajuan ke Supabase setiap N file


# ─── Supabase ────────────────────────────────────────────────

def _sb_headers(extra=None):
    h = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_SERVICE_KEY,
        'Content-Type': 'application/json',
        'User-Agent': 'PINUS-OKR-Migrasi',
    }
    if extra:
        h.update(extra)
    return h


def sb_siap():
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def sb_ambil():
    """Ambil data OKR dari Supabase. None kalau baris belum ada."""
    url = SUPABASE_URL.rstrip('/') + '/rest/v1/okr_state?id=eq.main&select=data,ts'
    req = urllib.request.Request(url, headers=_sb_headers())
    with urllib.request.urlopen(req, timeout=60) as resp:
        rows = json.loads(resp.read().decode('utf-8'))
    if not rows:
        return None
    d = rows[0].get('data') or {}
    if rows[0].get('ts') and not d.get('_ts'):
        d['_ts'] = int(rows[0]['ts'])
    return d


def sb_simpan(data):
    """Upsert baris 'main'."""
    url = SUPABASE_URL.rstrip('/') + '/rest/v1/okr_state?on_conflict=id'
    row = [{
        'id': 'main',
        'data': data,
        'ts': int(data.get('_ts') or datetime.now().timestamp() * 1000),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }]
    body = json.dumps(row, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url, data=body, method='POST',
        headers=_sb_headers({'Prefer': 'resolution=merge-duplicates,return=minimal'}))
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status


# ─── Bantu ───────────────────────────────────────────────────

def unduh(url, timeout=90):
    req = urllib.request.Request(url, headers={'User-Agent': 'PINUS-OKR-Migrasi'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers.get('Content-Type', '')


def kumpulkan_url(data):
    """Semua URL GitHub yang masih ada di dalam data (unik, urut stabil)."""
    teks = json.dumps(data, ensure_ascii=False)
    hasil, terlihat = [], set()
    for u in RAW_RE.findall(teks):
        if u not in terlihat:
            terlihat.add(u)
            hasil.append(u)
    return hasil


def key_dari_url(u):
    """uploads/<divisi>/<file> — diambil dari path URL GitHub-nya."""
    polos = urllib.parse.unquote(u)
    m = re.search(r'/uploads/([^/]+)/([^/?#]+)$', polos)
    if m:
        divisi = re.sub(r'[^A-Za-z0-9._-]+', '_', m.group(1))
        nama = re.sub(r'[^A-Za-z0-9._-]+', '_', m.group(2))
        return 'uploads/{}/{}'.format(divisi, nama)
    nama = re.sub(r'[^A-Za-z0-9._-]+', '_', polos.rsplit('/', 1)[-1].split('?')[0])
    return 'uploads/umum/' + nama


def ganti_url(data, dari, ke):
    teks = json.dumps(data, ensure_ascii=False)
    teks = teks.replace(json.dumps(dari)[1:-1], json.dumps(ke)[1:-1])
    return json.loads(teks)


def mime_dari(nama, bawaan):
    ext = (re.search(r'\.([A-Za-z0-9]{1,5})$', nama) or [None, ''])[1].lower()
    return {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif',
        'webp': 'image/webp', 'pdf': 'application/pdf', 'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
    }.get(ext) or bawaan or 'application/octet-stream'


# ─── Perintah ────────────────────────────────────────────────

def cmd_cek():
    print('Supabase   :', 'siap' if sb_siap() else 'BELUM — isi SUPABASE_URL & SUPABASE_SERVICE_KEY di local_config.py')
    print('Backblaze  :', 'siap' if b2py.siap() else 'BELUM — isi B2_KEY_ID, B2_APP_KEY, B2_BUCKET, B2_ENDPOINT di local_config.py')
    if not sb_siap():
        return 1
    try:
        data = sb_ambil()
    except urllib.error.HTTPError as e:
        pesan = e.read().decode(errors='replace')[:300]
        print('\nGagal baca Supabase: HTTP', e.code, pesan)
        if 'does not exist' in pesan or e.code == 404:
            print('→ Tabel okr_state belum dibuat. Jalankan SQL di MIGRASI.md lewat SQL Editor Supabase.')
        return 1
    except Exception as e:
        print('\nGagal baca Supabase:', e)
        return 1

    if data is None:
        print('\nSupabase  : tabel ada, tapi data OKR BELUM dipindah (baris "main" kosong)')
        print('→ Jalankan: py migrasi_ke_cloud.py --data')
        return 0

    sisa = kumpulkan_url(data)
    kunci = [k for k in data.keys() if k != '_ts']
    print('\nSupabase  : berisi {} kunci data'.format(len(kunci)))
    print('File di B2: {} sudah dipindah'.format(len(set(re.findall(r'/api/file\?k=(uploads/[^"\']+)', json.dumps(data))))))
    print('Sisa file GitHub yang belum dipindah:', len(sisa))
    if sisa:
        for u in sisa[:3]:
            print('   -', u.rsplit('/', 1)[-1])
        print('→ Jalankan: py migrasi_ke_cloud.py --file')
    else:
        print('→ Semua file sudah di B2. GitHub aman untuk dihapus.')
    if b2py.siap():
        try:
            print('Isi bucket :', len(b2py.list_objects()), 'objek (maks 1000 ditampilkan)')
        except Exception as e:
            print('Isi bucket : gagal dibaca —', e)
    return 0


def cmd_data(paksa=False, sumber=None):
    if not sb_siap():
        print('SUPABASE_URL / SUPABASE_SERVICE_KEY belum diisi di local_config.py')
        return 1
    lama = sb_ambil()
    if lama and not paksa:
        print('Supabase sudah berisi {} kunci. Tambahkan --paksa kalau memang ingin ditimpa.'
              .format(len([k for k in lama if k != '_ts'])))
        return 1

    asal = sumber or GH_RAW_DATA
    print('Mengambil data dari:', asal)
    if asal.startswith('http'):
        isi, _ = unduh(asal + ('&' if '?' in asal else '?') + '_=' + str(int(datetime.now().timestamp())))
        teks = isi.decode('utf-8')
    else:
        with open(asal, 'r', encoding='utf-8') as f:
            teks = f.read()

    if '"__CLOUD__"' in teks:
        print('DIBATALKAN: sumber mengandung placeholder __CLOUD__ (file belum termuat).')
        return 1
    data = json.loads(teks)
    print('  {} kunci, {} KB, {} file menunggu dipindah'
          .format(len([k for k in data if k != '_ts']), len(teks) // 1024, len(kumpulkan_url(data))))
    sb_simpan(data)
    print('Selesai — data OKR sudah ada di Supabase.')
    print('→ Lanjut: py migrasi_ke_cloud.py --file')
    return 0


def cmd_file(limit=None, dry=False):
    if not sb_siap():
        print('SUPABASE_URL / SUPABASE_SERVICE_KEY belum diisi di local_config.py')
        return 1
    if not b2py.siap():
        print('Kredensial B2 belum diisi di local_config.py')
        return 1
    data = sb_ambil()
    if data is None:
        print('Data OKR belum ada di Supabase. Jalankan dulu: py migrasi_ke_cloud.py --data')
        return 1

    sisa = kumpulkan_url(data)
    if not sisa:
        print('Tidak ada file GitHub yang tersisa. Semua sudah di B2.')
        return 0
    if limit:
        sisa = sisa[:limit]

    print('Akan memindahkan {} file ke bucket {}\n'.format(len(sisa), b2py.B2_BUCKET))
    if dry:
        for u in sisa:
            print('  [dry]', key_dari_url(u))
        return 0

    berhasil = gagal = 0
    total_byte = 0
    daftar_gagal = []
    for i, u in enumerate(sisa, 1):
        key = key_dari_url(u)
        try:
            isi, ctype = unduh(u)
            b2py.put_object(key, isi, mime_dari(key, ctype))
            data = ganti_url(data, u, '/api/file?k=' + key)
            berhasil += 1
            total_byte += len(isi)
            print('  [{}/{}] OK  {} ({:,} byte)'.format(i, len(sisa), key, len(isi)))
        except Exception as e:
            gagal += 1
            daftar_gagal.append((u, str(e)[:150]))
            print('  [{}/{}] GAGAL {} — {}'.format(i, len(sisa), key, str(e)[:150]))

        # simpan kemajuan berkala supaya aman kalau terputus
        if berhasil and berhasil % SIMPAN_TIAP == 0:
            data['_ts'] = int(datetime.now().timestamp() * 1000)
            sb_simpan(data)
            print('        … kemajuan disimpan ({} file)'.format(berhasil))

    if berhasil:
        data['_ts'] = int(datetime.now().timestamp() * 1000)
        sb_simpan(data)

    print('\nSelesai: {} berhasil, {} gagal, {:,} byte terkirim'.format(berhasil, gagal, total_byte))
    tersisa = len(kumpulkan_url(sb_ambil() or {}))
    print('Sisa file yang belum dipindah:', tersisa)
    if daftar_gagal:
        print('\nYang gagal (jalankan ulang perintah ini untuk mencoba lagi):')
        for u, sebab in daftar_gagal[:10]:
            print('  -', u.rsplit('/', 1)[-1], '→', sebab)
    return 0


def main():
    p = argparse.ArgumentParser(description='Migrasi OKR: GitHub → Supabase + Backblaze B2')
    p.add_argument('--cek', action='store_true', help='periksa kesiapan & hitung pekerjaan')
    p.add_argument('--data', action='store_true', help='pindahkan data OKR ke Supabase')
    p.add_argument('--file', action='store_true', help='pindahkan file ke B2 lalu tulis ulang URL-nya')
    p.add_argument('--limit', type=int, default=None, help='batasi jumlah file per jalan')
    p.add_argument('--paksa', action='store_true', help='timpa data Supabase yang sudah ada (dgn --data)')
    p.add_argument('--sumber', default=None, help='sumber data OKR: URL atau path file lokal')
    p.add_argument('--dry-run', action='store_true', help='tampilkan rencana tanpa mengunggah')
    a = p.parse_args()

    if a.data:
        return cmd_data(paksa=a.paksa, sumber=a.sumber)
    if a.file:
        return cmd_file(limit=a.limit, dry=a.dry_run)
    return cmd_cek()


if __name__ == '__main__':
    sys.exit(main())
