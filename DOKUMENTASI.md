# Dokumentasi Tools OKR Pinus Packindo

> **Tujuan dokumen:** Catatan arsitektur & cara kerja aplikasi agar update berikutnya
> mudah diperbaiki tanpa mulai dari nol. Status per Juni 2026: **stabil & berjalan baik.**

---

## 1. Gambaran Umum

Aplikasi web **single-page** untuk mengelola OKR (Objective & Key Result), TAL
(Task Achievement List), dan data operasional bulanan per divisi di Pinus Packindo.

- **Frontend:** satu file HTML besar berisi semua HTML + CSS + JavaScript (inline).
- **Hosting:** Vercel (static) → URL produksi: `https://pinuspackindo-okr.vercel.app`
- **Penyimpanan data:** `localStorage` browser + sinkronisasi ke **GitHub** (file `okr_data.json`)
  lewat serverless function `api/okr.js`.
- **Tidak ada database** — sumber kebenaran data adalah `okr_data.json` di repo GitHub.

---

## 2. File Penting

| File | Fungsi |
|------|--------|
| `index.html` | **Versi utama** yang dipakai Vercel (static). Berisi seluruh aplikasi. |
| `templates/index.html` | **Salinan kembar** untuk Flask (`app.py`). **WAJIB diubah bersamaan dengan `index.html`.** |
| `api/okr.js` | Serverless function Vercel: GET/POST `okr_data.json` ke GitHub. Pakai `GITHUB_TOKEN` dari env Vercel. |
| `okr_data.json` | Data tersimpan (di-commit otomatis oleh auto-sync). |
| `vercel.json` | Konfigurasi header `no-cache` agar browser selalu ambil versi terbaru. |
| `app.py` | Flask server (untuk dev lokal). **Catatan: app.py saat ini melayani app lain ("Payroll"), bukan OKR.** OKR jalan sebagai static `index.html`. |
| `local_config.py` | **Gitignored.** Tempat `GITHUB_TOKEN` lokal. JANGAN commit token. |
| `patch_*.py` | Skrip Python untuk menerapkan perubahan ke kedua file HTML sekaligus (lihat bagian 9). |

> ⚠️ **PENTING:** `index.html` dan `templates/index.html` harus selalu sinkron.
> Setiap perubahan kode diterapkan ke **KEDUANYA**.

---

## 3. Arsitektur Data

### 3.1 Variabel utama
- `okrData` — objek besar tempat semua data disimpan (di-load dari localStorage).
- `okrSaveLS()` — simpan ke localStorage **dan** POST ke cloud (`/api/okr`).
- `okrLoad()` — baca dari localStorage.
- `APP_CUR_USER` — username yang sedang login.

### 3.2 Format key di `okrData`
| Prefix | Modul | Generator |
|--------|-------|-----------|
| `2026-05`, `2026-06` | OKR Dashboard (per bulan, objek keyed per divisi) | `okrKey()` |
| `_s_<sub>_<y>_<m>` | Store | `_sk` |
| `_d_<sub>_<y>_<m>` | Distribution Sales | `_dk` |
| `_w_<sub>_<y>_<m>` | Warehouse | `_wk` |
| `_inv_<sub>_<y>_<m>`, `_inv_rn_do_*`, `_inv_rot_*` | Inventory | `_ik`, dst |
| `_p_ins_*`, `_p_apo_*`, `_p_kpen_*`, `_p_sv_*`, `_p_ir_*` | Purchasing | `_pkIns`, `_pkApo`, dst |
| `_fa_<sub>_*`, `_fa_rot_*` | Finance & Accounting | `_fak`, `_farotKey` |
| `_ga_so_*`, `_ga_wp_*`, `_ga_rot_*` | General Affair | `_gasoKey`, dst |
| `_hrd_kdk_*`, `_hrd_<sub>_*`, `_hrd_rec_*`, `_hrd_kin_*` | HRD | `_hrdKdkKey`, dst |
| `_ia_reko_*`, `_ia_rot_<type>_*`, `_ia_proj_*` | Internal Audit | `iaRekoKey`, dst |
| `_tal_d<idx>_<y>_<m>` | TAL (per divisi index) | `_talKey` |
| `_userAccess`, `_userPwd`, `_customUsers`, `_disabledUsers` | Data akun (dikelola Admin) | — |
| `_ts` | Timestamp sinkronisasi | — |

### 3.3 Sinkronisasi cloud (penting & sensitif)
- Saat halaman load, `okrInit()` fetch `/api/okr`; jika kosong, fallback ke
  `raw.githubusercontent.com/.../okr_data.json`.
- Logika merge: ambil cloud jika `cloudTs > localTs`, **tapi selalu** ambil key
  admin (`_userAccess` dll) dan `_tal_*` dari cloud (source of truth) tanpa cek timestamp.
- `talInit()` melakukan **fresh-fetch** TAL setiap kali modul TAL dibuka.
- `okrSaveLS()` ada guard: tidak POST saat `_okrSyncBlocked=true` (cegah wipe saat initial load)
  dan tidak POST jika data kosong.

---

## 4. Modul & Fungsi Render

Pola umum tiap modul: `xInit()` (setup tahun/bulan + dropdown) → `xRender()` (gambar tabel)
→ `xShowSub()` (ganti sub-tab). Navigasi lewat `showPanel(name, btn)`.

| Modul | Init | Render | Catatan |
|-------|------|--------|---------|
| Dashboard OKR | `okrInit` | `okrRender` | Sinkron semua sub-modul → OKR; hitung Score Global |
| TAL | `talInit` | `talRender` / `talBuildDivCard` | Multi-divisi, akses per-user |
| Store | `storeInit` | `storeRender` | |
| Distribution Sales | `distribInit` | `distribRender` | |
| Warehouse | `warehouseInit` | `warehouseRender` | |
| Inventory | `inventoryInit` | `invRender*` | |
| Purchasing | `purchasingInit` | `purchInstockRender`, `purchApoRender`, dst | |
| Finance & Accounting | `finaccInit` | `finaccRender*` | |
| General Affair | `gaInit` | `gaRender*` | |
| HRD | `hrdInit` | `hrdRender*` | |
| Internal Audit | `iaInit` | `iaRekoRender`, `iaRotRender`, `iaProjRender` | Selalu reset ke bulan berjalan |
| Pengaturan | `pengaturanInit` | `pengaturanRender`, `accessRender` | User Access khusus Admin |

---

## 5. Akses & Role (Auth)

- Login: dropdown username + password (`doLogin`). Session di `sessionStorage`.
- **`ACCESS_DEFAULT`** — akses default tiap user (modul mana yang terlihat + `okrAll`).
- **`okrData._userAccess`** — override akses yang diatur Admin (menang atas default).
- **`MODULE_OKR_DIV`** — peta modul → nama divisi OKR.
- **`MODULE_TAL_DIV`** — peta modul → index divisi TAL. **Sumber tunggal** untuk:
  - `authGetVisibleTALDivs()` — divisi TAL yang boleh dilihat
  - `authCanFillTALProgress(d)` — divisi TAL yang boleh diisi progress-nya
- Helper: `isOwnerOrAdmin()`, `isAdminUser()`, `authCanAccess(modul)`, `authCanSeeAllOKR()`.

**Aturan TAL yang berlaku sekarang:**
- Owner/Admin: lihat & isi semua divisi.
- Internal Audit (`okrAll:true`): lihat semua, isi divisi sendiri saja.
- User ops lain (Store, HRD, Inventory, dll): hanya lihat & isi **divisi sendiri**.
- Edit/tambah/hapus TAL hanya Owner/Admin.

**TAL_DIV_NAMES (index → nama divisi):**
`0 STORE, 1 MARKETING, 2 FINANCE & ACCOUNTING, 3 HRD, 4 GENERAL AFFAIR, 5 PURCHASING,
6 IT, 7 OPERASIONAL, 8 MANAGEMENT, 9 DISTRIBUTION SALES, 10 WAREHOUSE, 11 INVENTORY,
12 INTERNAL AUDIT`
> ⚠️ Tambah divisi baru **selalu di akhir array** agar index lama tak bergeser (data lama aman).

---

## 6. Pola Umum (dipakai banyak modul)

### 6.1 Upload bukti
- Maks **3 file** per upload, tiap file maks **500 KB**.
- Helper `_processImgFiles(files, cb)` — kompres gambar (canvas, JPEG 0.78, maks 1400×1050),
  fallback FileReader untuk non-gambar. Hasil: `[{name, data}]`.
- Data tersimpan di `d.evidences[]` (semua file) + `d.evidence`/`d.evidenceName` (file pertama, backward-compat).
- Validasi standar tiap fungsi upload:
  ```js
  var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;
  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}
  if(_fs.some(function(f){return f.size>500*1024;})){notify('Ukuran file maksimal 500 KB per file.','error');inp.value='';return;}
  ```

### 6.2 Lihat bukti
- `_viewEvs(evs)` — 1 file gambar → modal; 1 file non-gambar → download; banyak file → overlay tombol per file.
- Fungsi `xViewEv*` mengumpulkan array `evidences` lalu panggil `_viewEvs`.

### 6.3 Tombol aksi standar (warna)
- Simpan: `background:var(--primary);color:#fff`
- Edit: `border:1.5px solid var(--border);color:var(--text-m)` + ✏️
- Hapus: `border:1.5px solid #fca5a5;color:#dc2626` + 🗑

### 6.4 Variabel CSS penting
`--primary, --border, --text, --text-m, --text-l, --bg, --bg2, --success, --danger, --radius-sm`.
Alias (jangan dihapus): `--acc=--primary`, `--tx=--text`, `--tx2=--text-m`, `--tx3=--text-l`, `--brd=--border`.
(Modul Internal Audit memakai alias ini.)

---

## 7. Catatan Khusus Tiap Modul (hasil perbaikan terakhir)

- **Score Global OKR** = rata-rata Score Akhir **semua** divisi (sama untuk semua user).
- **Distribution Sales → Customer Retention**: satuan **%** (bukan "orang").
- **Internal Audit → Project Baru**: score OKR = **jumlah project** (3 project → 3), bukan persentase.
- **Internal Audit**: selalu buka di bulan berjalan; tombol hapus 🗑 di tiap sub-modul;
  upload tidak mereset input yang sudah diisi.
- **Purchasing → Akurasi PO**: butuh konstanta `ACC_KW` (daftar keyword Source Origin tidak akurat).
  **JANGAN dihapus**: `['HPP','SUPPLIER','HARGA','KUANTITI','QTY','SALAH','DISKON','LEBIH','KURANG','TEMPO','TERMIN','NAMA']`.
- **Purchasing → In Stock**: Score = rata-rata skor harian; bisa isi skor manual tanpa wajib upload file.

---

## 8. Deployment (Vercel) — PENTING

- Push ke branch `main` di GitHub → Vercel auto-deploy.
- **Masalah umum:** bot auto-sync membuat banyak commit beruntun (sebagian ber-tag
  `[vercel skip]`). Kadang Vercel **tidak** men-deploy commit "Auto sync".
- **Cara paksa deploy** (terbukti bekerja): buat commit kosong dengan pesan normal:
  ```bash
  git commit --allow-empty -m "deploy: force Vercel rebuild"
  git push origin main
  ```
- **Cache:** sudah dipasang `no-cache` (`vercel.json` + meta tag). Browser selalu ambil
  versi terbaru. Header live: `Cache-Control: no-cache, must-revalidate, max-age=0`.
- **Cek deploy berhasil:** fetch live & cari penanda perubahan, mis.
  ```bash
  curl -s "https://pinuspackindo-okr.vercel.app/?cb=$RANDOM" | grep -c "<penanda kode baru>"
  ```

---

## 9. Cara Aman Melakukan Update

1. **Selalu ubah KEDUA file**: `index.html` dan `templates/index.html`.
   Untuk perubahan banyak/berulang, pakai skrip Python (lihat contoh `patch_*.py`):
   - Definisikan pasangan `(old_string, new_string)` yang **persis** cocok.
   - Loop ke kedua file, ganti, simpan hanya jika semua cocok.
2. **Verifikasi sebelum commit** (hindari syntax error yang membuat semua modul kosong):
   - Jalankan preview static dan compile script utama, mis. via tool preview
     (`new Function(scriptBody)` harus `OK`), atau cek fungsi `typeof window.showPanel === 'function'`.
   - Gejala syntax error: **semua modul kosong + dropdown kosong + topbar tidak update**
     (= seluruh `<script>` gagal parse → fungsi tak terdefinisi).
3. **Commit + push**, lalu **paksa deploy** dengan commit kosong (bagian 8).
4. **Verifikasi live** dengan `curl` + grep penanda.
5. Hard refresh sekali (`Ctrl+Shift+R`) — setelah no-cache aktif, refresh biasa cukup.

---

## 10. Keamanan

- **`GITHUB_TOKEN` TIDAK BOLEH** ada di file yang di-commit. Hanya di:
  - `local_config.py` (gitignored) untuk dev lokal, dan
  - **Environment Variables Vercel** untuk produksi.
- Catatan: `.git/config` lokal mungkin menyimpan token di URL remote (untuk auth HTTPS).
  Itu file lokal (tidak ter-commit), tapi sebaiknya token di-rotate berkala.

---

## 11. Troubleshooting Cepat

| Gejala | Kemungkinan penyebab | Solusi |
|--------|----------------------|--------|
| Semua modul kosong, dropdown kosong, topbar tak update | Syntax error JS / JS belum termuat | Compile script; cek perubahan terakhir; pastikan kedua file valid |
| Modul kosong setelah deploy, tapi kode valid | Cache browser / Vercel belum deploy | Hard refresh; cek Vercel "Ready"; paksa deploy commit kosong |
| Data divisi tak muncul untuk user tertentu | Akses `_userAccess` / `MODULE_TAL_DIV` | Cek centang akses di Pengaturan; cek mapping |
| Error "X is not defined" saat aksi | Konstanta hilang (mis. `ACC_KW`) | Cari definisi yang hilang; kembalikan |
| Deploy tak jalan | Commit ber-tag `[vercel skip]` jadi HEAD | Commit kosong pesan normal |

---

*Dokumen ini dibuat sebagai titik acuan. Perbarui bila ada perubahan arsitektur besar.*
