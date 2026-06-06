# Peta Bagian Dashboard OKR

> Tujuan: tiap bagian dipecah supaya perbaikan bisa langsung ke titiknya — cukup sebut
> **kode bagian** (mis. "perbaiki B3c") tanpa harus cek semua.
> Nomor baris bisa bergeser saat file diedit; **nama fungsi** adalah patokan yang stabil.

---

## A. TAMPILAN / STRUKTUR HTML  (cari: `id="panel-dashboard"`)

| Kode | Bagian | Lokasi (anchor) |
|------|--------|-----------------|
| **A1** | Header + filter Bulan/Tahun + tombol **‹ ›**, Template, Import Excel, + New OKR | `id="panel-dashboard"` (≈ baris 409) |
| **A2** | Wadah **kartu Score Global** | `id="okr-global-wrap"` (≈ 432) |
| **A3** | Wadah **tabel semua divisi** | `id="okr-tables-wrap"` (≈ 436) |
| **A4** | **Modal Tambah/Edit OKR** (form KR, target, bobot) | `id="okr-modal"` (≈ 837), select bulan `id="okr-f-bulan"` (≈ 863) |

---

## B. LOGIKA (JavaScript)

### B1. Muat & Simpan Data (sinkronisasi cloud)
| Kode | Fungsi | Baris | Untuk apa |
|------|--------|-------|-----------|
| **B1a** | `okrLoad()` | 4128 | Baca data dari localStorage |
| **B1b** | `okrSaveLS()` | 4185 | Simpan ke localStorage + upload file ke GitHub + POST ke cloud |
| **B1c** | `okrLoadCloud()` | 4236 | Tarik data dari cloud (tombol/manual) |
| **B1d** | `okrInit()` | 4251 | Saat halaman load: baca lokal → render → tarik cloud → adopt |
| **B1e** | `_okrFlushUploads()` / `okrUploadFile()` | 4146 | Upload file bukti ke GitHub jadi URL (anti-bloat) |

### B2. Navigasi Bulan
| Kode | Fungsi | Baris |
|------|--------|-------|
| **B2** | `okrPrevMonth()` / `okrNextMonth()` | 4347 / 4351 |

### B3. Render Utama — `okrRender()` (baris 4357)
| Kode | Sub-bagian | Baris | Untuk apa |
|------|-----------|-------|-----------|
| **B3a** | **Sync sub-modul → OKR** | 4358–4430 | Tarik nilai dari modul lain ke "Actual" OKR. Per divisi: Inventory(4358), Purchasing In Stock(4365), Purchasing bulanan(4367), Finance(4376), General Affair(4393), HRD(4404), Internal Audit(4419) |
| **B3b** | **Empty state** ("Belum ada OKR") | ≈ 4445 | Tampilan saat belum ada data |
| **B3c** | **Hitung Score Global** (rata-rata semua divisi) | 4451–4462 | Akumulasi Score Akhir semua divisi |
| **B3d** | **Loop kartu per-divisi** (Objective + tabel KR + Score Akhir + Action Plan) | 4464+ | Gambar tiap kartu divisi |
| **B3e** | **Render kartu Score Global** (warna/teks Kritis/Baik) | ≈ 4536+ | Tampilan kartu global |

> Rumus Score per KR: `Actual / Target × Bobot`. Score Akhir divisi = jumlah semua KR.

### B4. Tambah / Edit OKR (modal)
| Kode | Fungsi | Baris |
|------|--------|-------|
| **B4a** | `okrOpenNew()` | 4641 |
| **B4b** | `okrOpenEdit()` | 4659 |
| **B4c** | `okrAddRow()` / `okrDelRow()` | 4688 / 4715 |
| **B4d** | `okrUpdateBobotWarn()` (peringatan total bobot) | 4720 |
| **B4e** | `okrSave()` (simpan KR) | 4733 |
| **B4f** | `okrCloseModal()` | 4681 |

### B5. Hapus / Duplikat Divisi
| Kode | Fungsi | Baris |
|------|--------|-------|
| **B5a** | `okrDeleteDivisi()` | 4626 |
| **B5b** | `okrDuplicate()` (duplikat bulan lalu) | 4593 |

### B6. Import Excel / Template
| Kode | Fungsi | Baris |
|------|--------|-------|
| **B6a** | `okrImportClick()` | 4795 |
| **B6b** | `okrDownloadTemplate()` | 4799 |
| **B6c** | `okrProcessFile()` | 4818 |
| **B6d** | `okrImportRows()` | 4858 |

### B7. Helper
| Kode | Fungsi | Baris |
|------|--------|-------|
| **B7** | `okrEsc`(4573), `okrFmt`(4574), `okrGetRows`(4582), `okrGetAP`(4587), `okrKey`(4223) | — |

---

## Cara pakai
Cukup bilang, misalnya:
- "**Perbaiki B3c**" → ubah cara hitung Score Global.
- "**B3a sync HRD salah**" → cek blok sync HRD di okrRender (≈ 4404).
- "**B4e**" → logika simpan OKR.
- "**A1**" → tata letak header/tombol dashboard.

Saya langsung ke bagian itu tanpa cek seluruh file.

---
*Catatan: ada DUA file kembar — `index.html` (dipakai Vercel) & `templates/index.html`.
Setiap perbaikan diterapkan ke keduanya.*
