"""
patch_slim_fix.py
Perbaikan bug: _slim flag menyebabkan cloud selalu menang saat reload,
sehingga perubahan lokal yang belum ter-POST ke cloud selalu tertimpa.

Root cause:
  if(cloudTs>localTs||localEmpty||okrData._slim){  ← _slim selalu true setelah save

Fix:
  1. Hapus ||okrData._slim dari kedua kondisi (main path & raw fallback)
  2. Tambah helper _okrRestoreSlim(src) untuk merestorasi __CLOUD__ placeholder
     dari cloud tanpa menimpa data lokal yang lebih baru
  3. Panggil _okrRestoreSlim jika local menang tapi _slim=1
"""

import re

FILES = [
    r'index.html',
    r'templates\index.html',
]

# ─── PATCH 1: Tambah helper _okrRestoreSlim sebelum okrSaveLS ─────────────────
HELPER_FUNC = """function _okrRestoreSlim(src){
  // Ganti semua __CLOUD__ placeholder di okrData dengan nilai asli dari src (cloud/raw).
  // Hanya replace placeholder — tidak menimpa data lokal lain.
  if(!src||typeof src!=='object') return;
  function _deepRestore(local,remote){
    if(!local||typeof local!=='object'||!remote||typeof remote!=='object') return;
    Object.keys(local).forEach(function(k){
      if(local[k]==='__CLOUD__'&&k in remote) local[k]=remote[k];
      else if(local[k]&&typeof local[k]==='object') _deepRestore(local[k],remote[k]);
    });
  }
  _deepRestore(okrData,src);
  delete okrData._slim;
  try{var _k=(typeof OKR_STORE_KEY!=='undefined'&&OKR_STORE_KEY)?OKR_STORE_KEY:'pinus_okr_v1';localStorage.setItem(_k,JSON.stringify(okrData));}catch(e){}
}
"""

# ─── PATCH 2: Raw fallback path — hapus ||okrData._slim & tambah else-slim ────
OLD_RAW = (
    "          if(rawTs>localTs||localDataKeys.length===0||okrData._slim){\n"
    "            // Raw lebih baru — tapi pertahankan data sub-modul lokal yg tidak ada di raw (cegah wipe)\n"
    "            var _lSub={};localDataKeys.forEach(function(k){if(k.startsWith('_'))_lSub[k]=okrData[k];});\n"
    "            okrData=raw;Object.keys(_lSub).forEach(function(k){if(!(k in raw))okrData[k]=_lSub[k];});\n"
    "            localStorage.setItem(OKR_STORE_KEY,JSON.stringify(okrData));okrRender();talRender();authApplyAccess();\n"
    "          } else if(localOkrKeys.length===0){"
)
NEW_RAW = (
    "          if(rawTs>localTs||localDataKeys.length===0){\n"
    "            // Raw lebih baru — tapi pertahankan data sub-modul lokal yg tidak ada di raw (cegah wipe)\n"
    "            var _lSub={};localDataKeys.forEach(function(k){if(k.startsWith('_'))_lSub[k]=okrData[k];});\n"
    "            okrData=raw;Object.keys(_lSub).forEach(function(k){if(!(k in raw))okrData[k]=_lSub[k];});\n"
    "            localStorage.setItem(OKR_STORE_KEY,JSON.stringify(okrData));okrRender();talRender();authApplyAccess();\n"
    "          } else if(okrData._slim){\n"
    "            // Local lebih baru tapi slim — restore __CLOUD__ dari raw tanpa timpa data lokal\n"
    "            _okrRestoreSlim(raw);\n"
    "          } else if(localOkrKeys.length===0){"
)

# ─── PATCH 3: Main cloud path — hapus ||okrData._slim & tambah else-slim ──────
OLD_CLOUD = (
    "      if(cloudTs>localTs||localEmpty||okrData._slim){\n"
    "        // Cloud lebih baru — tapi pertahankan data sub-modul lokal yg tidak ada di cloud (cegah wipe)\n"
    "        var _localSub={};\n"
    "        if(!localEmpty){localDataKeys.forEach(function(k){if(k.startsWith('_'))_localSub[k]=okrData[k];});}  \n"
    "        okrData=cloud;\n"
    "        Object.keys(_localSub).forEach(function(k){if(!(k in cloud))okrData[k]=_localSub[k];});\n"
    "        localStorage.setItem(OKR_STORE_KEY,JSON.stringify(okrData));\n"
    "        okrRender();talRender();authApplyAccess();\n"
    "        if(localTs>0&&!localEmpty) notify('Data diperbarui dari cloud ✓');\n"
    "      } else if(localOkrKeys.length===0&&cloudOkrKeys.length>0){"
)
NEW_CLOUD = (
    "      if(cloudTs>localTs||localEmpty){\n"
    "        // Cloud lebih baru — tapi pertahankan data sub-modul lokal yg tidak ada di cloud (cegah wipe)\n"
    "        var _localSub={};\n"
    "        if(!localEmpty){localDataKeys.forEach(function(k){if(k.startsWith('_'))_localSub[k]=okrData[k];});}  \n"
    "        okrData=cloud;\n"
    "        Object.keys(_localSub).forEach(function(k){if(!(k in cloud))okrData[k]=_localSub[k];});\n"
    "        localStorage.setItem(OKR_STORE_KEY,JSON.stringify(okrData));\n"
    "        okrRender();talRender();authApplyAccess();\n"
    "        if(localTs>0&&!localEmpty) notify('Data diperbarui dari cloud ✓');\n"
    "      } else if(okrData._slim){\n"
    "        // Local lebih baru tapi slim — restore __CLOUD__ dari cloud tanpa timpa data lokal\n"
    "        _okrRestoreSlim(cloud);\n"
    "      } else if(localOkrKeys.length===0&&cloudOkrKeys.length>0){"
)

# Target untuk menyisipkan helper (sebelum fungsi okrSaveLS)
ANCHOR_BEFORE_SAVE = "function okrSaveLS(){"

def apply_patch(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    original = text

    # Patch 2: raw fallback
    if OLD_RAW in text:
        text = text.replace(OLD_RAW, NEW_RAW, 1)
        print(f"  [OK] Patch 2 (raw fallback) applied: {path}")
    else:
        print(f"  [SKIP] Patch 2 tidak cocok (sudah dipatch?): {path}")

    # Patch 3: main cloud path
    if OLD_CLOUD in text:
        text = text.replace(OLD_CLOUD, NEW_CLOUD, 1)
        print(f"  [OK] Patch 3 (main cloud) applied: {path}")
    else:
        print(f"  [SKIP] Patch 3 tidak cocok (sudah dipatch?): {path}")

    # Patch 1: sisipkan helper sebelum okrSaveLS (hanya jika belum ada)
    if '_okrRestoreSlim' not in text:
        if ANCHOR_BEFORE_SAVE in text:
            text = text.replace(ANCHOR_BEFORE_SAVE, HELPER_FUNC + ANCHOR_BEFORE_SAVE, 1)
            print(f"  [OK] Patch 1 (helper _okrRestoreSlim) inserted: {path}")
        else:
            print(f"  [FAIL] Anchor tidak ditemukan: {path}")
    else:
        print(f"  [SKIP] Patch 1 sudah ada: {path}")

    if text == original:
        print(f"  [INFO] Tidak ada perubahan: {path}")
        return

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"  [SAVED] {path}")

if __name__ == '__main__':
    for p in FILES:
        print(f"\nPatching: {p}")
        apply_patch(p)
    print("\nSelesai.")
