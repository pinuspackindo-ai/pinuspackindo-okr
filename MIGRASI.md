# Migrasi GitHub → Supabase + Backblaze B2

## Cara cepat: jalankan dari laptop, tanpa Vercel

Ini jalur yang dipakai sekarang. Vercel tidak perlu disentuh sama sekali.

**1. Buat tabel di Supabase** — SQL di [Langkah 1](#langkah-1--buat-tabel-di-supabase) di bawah,
tempel di SQL Editor Supabase, klik Run. Sekali saja.

**2. Buat Application Key di Backblaze** — lihat [Langkah 2](#langkah-2--buat-application-key-di-backblaze).

**3. Isi kredensial di laptop** — salin `local_config.example.py` jadi `local_config.py`,
isi 5 nilai. File itu tidak masuk git.

**4. Jalankan migrasinya:**

```bash
py migrasi_ke_cloud.py --cek
```
```bash
py migrasi_ke_cloud.py --data
```
```bash
py migrasi_ke_cloud.py --file
```

`--cek` memeriksa kesiapan dan menghitung sisa pekerjaan. `--data` memindahkan
data OKR ke Supabase. `--file` memindahkan 606 file ke B2 lalu menulis ulang
URL-nya di data. Aman diulang — kalau terputus, jalankan lagi perintah yang sama.
Kemajuan disimpan tiap 10 file.

**5. Pakai dashboardnya** — jalankan `app.py` seperti biasa. Dia membaca data dari
Supabase dan menyajikan file dari B2 lewat `/api/file`.

Sisa dokumen di bawah adalah rincian tiap langkah, plus cara lewat Vercel kalau
suatu saat diperlukan.

---


Status: **kode siap, menunggu kredensial di-set.** Selama ENV belum diisi,
aplikasi tetap berjalan memakai GitHub seperti biasa (dwi-mode), jadi tidak ada
downtime. Begitu ENV terisi, penyimpanan otomatis berpindah.

| Apa | Dari | Ke |
|---|---|---|
| Data OKR (okr_data.json, 234 KB) | GitHub branch `data` | Supabase, tabel `okr_state` baris `id='main'` |
| File bukti & Excel (605 file) | GitHub `uploads/**` | Backblaze B2 bucket `pinuspackindo-okr` |
| Login aplikasi | — | **tidak berubah** |

---

## Langkah 1 — Buat tabel di Supabase

Buka project → **SQL Editor** → jalankan:

```sql
create table if not exists okr_state (
  id         text primary key,
  data       jsonb       not null default '{}'::jsonb,
  ts         bigint      not null default 0,
  updated_at timestamptz not null default now()
);

-- Kunci total dari akses publik: RLS aktif TANPA policy apa pun.
-- Hanya service_role key (dipakai server Vercel) yang bisa baca/tulis,
-- karena service_role melewati RLS. Kunci anon TIDAK bisa apa-apa.
alter table okr_state enable row level security;
```

## Langkah 2 — Buat Application Key di Backblaze

Bucket sudah ada: `pinuspackindo-okr` (Private, endpoint `s3.us-east-005.backblazeb2.com`).

**App Keys** → *Add a New Application Key*:
- Name: `vercel-okr`
- Allow access to Bucket: **pinuspackindo-okr** (jangan "All")
- Type of Access: **Read and Write**

Catat `keyID` dan `applicationKey` — applicationKey hanya tampil sekali.

CORS di bucket **tidak perlu diatur**: file dibaca lewat `/api/file` milik
aplikasi sendiri (proxy), jadi selalu satu origin.

## Langkah 3 — Set Environment Variables di Vercel

Project Settings → Environment Variables (Production + Preview):

| Nama | Nilai |
|---|---|
| `SUPABASE_URL` | `https://ivxfbpbwwyvkgijrkycj.supabase.co` |
| `SUPABASE_SERVICE_KEY` | service_role key (Supabase → Settings → API) |
| `B2_KEY_ID` | keyID dari Langkah 2 |
| `B2_APP_KEY` | applicationKey dari Langkah 2 |
| `B2_BUCKET` | `pinuspackindo-okr` |
| `B2_ENDPOINT` | `s3.us-east-005.backblazeb2.com` |
| `MIGRATE_TOKEN` | karangan sendiri, mis. 32 karakter acak |

`GITHUB_TOKEN` **jangan dihapus dulu** — masih dipakai untuk membaca data lama
saat migrasi, dan sebagai cadangan kalau ada yang perlu diulang.

Setelah disimpan, **Redeploy** sekali supaya ENV terbaca.

## Langkah 4 — Jalankan migrasi

Semua lewat URL (dijalankan di server Vercel, kredensial tidak keluar):

```
1. Cek kesiapan
   /api/migrate?token=TOKEN&step=status

2. Pindahkan data OKR
   /api/migrate?token=TOKEN&step=data

3. Pindahkan file, ulangi sampai "sisa": 0   (605 file, ~20 per panggilan)
   /api/migrate?token=TOKEN&step=files&limit=20
```

Aman diulang: file yang sudah pindah dilewati, URL di data ditulis ulang jadi
`/api/file?k=uploads/...`. Kalau ada yang gagal, namanya muncul di `gagal[]` dan
cukup panggil ulang `step=files`.

## Langkah 5 — Verifikasi sebelum GitHub dihapus

- `step=status` → `fileBelumDipindah: 0`
- Buka dashboard, cek beberapa bukti & Excel di tiap divisi masih bisa dibuka.
  Badge di sebelah nama file harus biru **B2**; kalau masih kuning **⚠ GitHub**
  berarti file itu belum termigrasi.
- Simpan satu data baru → pastikan tersimpan (berarti tulis ke Supabase jalan).
- Upload satu bukti baru → badge-nya harus **B2**.

## Langkah 6 — Setelah GitHub dihapus

Hapus `GITHUB_TOKEN` dari Vercel, lalu minta hapus jalur lama:
`lib/github_legacy.js`, cabang dwi-mode di `api/okr.js` & `api/upload.js`,
fallback `raw.githubusercontent` di `index.html`, dan `api/migrate.js`.

## Untuk dashboard lokal (Flask)

Isi `local_config.py` (file ini tidak masuk git):

```python
SUPABASE_URL = 'https://ivxfbpbwwyvkgijrkycj.supabase.co'
SUPABASE_SERVICE_KEY = '<service_role key>'
```

`app.py` sekarang membaca dari Supabase dan menulis ke Supabase + file lokal
`okr_data.json` sebagai cadangan offline.
