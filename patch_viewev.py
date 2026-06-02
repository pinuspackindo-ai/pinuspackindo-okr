import sys

files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

# _viewEvs: opens single file in modal/new tab, multiple files in an overlay list
VIEW_EVS = (
    "function _viewEvs(evs){\n"
    "  if(!evs||evs.length===0){notify('Tidak ada bukti.','error');return;}\n"
    "  if(evs.length===1){\n"
    "    var e0=evs[0];\n"
    "    if(e0.data&&e0.data.startsWith('data:image/')){\n"
    "      document.getElementById('sem-name').textContent=e0.name||'Bukti';\n"
    "      var _img=document.getElementById('sem-img');\n"
    "      _img.src=e0.data;_img.style.display='block';\n"
    "      document.getElementById('store-ev-modal').style.display='flex';\n"
    "    }else{\n"
    "      var _a=document.createElement('a');_a.href=e0.data;_a.download=e0.name||'bukti';\n"
    "      document.body.appendChild(_a);_a.click();document.body.removeChild(_a);\n"
    "    }\n"
    "    return;\n"
    "  }\n"
    "  var _old=document.getElementById('_evov');if(_old)_old.remove();\n"
    "  var _ov=document.createElement('div');_ov.id='_evov';\n"
    "  _ov.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.75);display:flex;align-items:center;justify-content:center;z-index:9999;';\n"
    "  _ov.onclick=function(ev){if(ev.target===_ov)_ov.remove();};\n"
    "  var _box=document.createElement('div');\n"
    "  _box.style.cssText='background:var(--bg);border-radius:var(--radius);padding:20px;min-width:260px;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,.4);';\n"
    "  var _ttl=document.createElement('div');\n"
    "  _ttl.style.cssText='font-size:13px;font-weight:700;color:var(--text);margin-bottom:14px;';\n"
    "  _ttl.textContent='Bukti Upload ('+evs.length+' file)';\n"
    "  _box.appendChild(_ttl);\n"
    "  evs.forEach(function(ef,ei){\n"
    "    var _btn=document.createElement('button');\n"
    "    _btn.style.cssText='display:block;width:100%;text-align:left;padding:8px 12px;border:1.5px solid var(--primary);background:none;color:var(--primary);border-radius:var(--radius-sm);cursor:pointer;font-size:12px;font-family:var(--font);margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';\n"
    "    var _isImg=ef.data&&ef.data.startsWith('data:image/');\n"
    "    _btn.textContent=(_isImg?'\U0001F441 ':'\U0001F4E5 ')+(ef.name||('File '+(ei+1)));\n"
    "    (function(ef){\n"
    "      _btn.onclick=function(){\n"
    "        if(ef.data&&ef.data.startsWith('data:image/')){\n"
    "          document.getElementById('sem-name').textContent=ef.name||'Bukti';\n"
    "          var _img=document.getElementById('sem-img');\n"
    "          _img.src=ef.data;_img.style.display='block';\n"
    "          _ov.remove();\n"
    "          document.getElementById('store-ev-modal').style.display='flex';\n"
    "        }else{\n"
    "          var _a=document.createElement('a');_a.href=ef.data;_a.download=ef.name||'bukti';\n"
    "          document.body.appendChild(_a);_a.click();document.body.removeChild(_a);\n"
    "        }\n"
    "      };\n"
    "    })(ef);\n"
    "    _box.appendChild(_btn);\n"
    "  });\n"
    "  var _cl=document.createElement('button');\n"
    "  _cl.style.cssText='padding:6px 16px;border:1.5px solid var(--border);background:none;color:var(--text-m);border-radius:var(--radius-sm);cursor:pointer;font-size:12px;font-family:var(--font);margin-top:4px;';\n"
    "  _cl.textContent='Tutup';\n"
    "  _cl.onclick=function(){_ov.remove();};\n"
    "  _box.appendChild(_cl);\n"
    "  _ov.appendChild(_box);\n"
    "  document.body.appendChild(_ov);\n"
    "}\n"
)

# Common modal block (multi-line, d.evidence) to replace:
MODAL_D_ML = (
    "  document.getElementById('sem-name').textContent=d.evidenceName||'Bukti';\n"
    "  var img=document.getElementById('sem-img');\n"
    "  if(d.evidence.startsWith('data:image')){img.src=d.evidence;img.style.display='block';}\n"
    "  else{img.style.display='none';}\n"
    "  document.getElementById('store-ev-modal').style.display='flex';"
)
MODAL_D_ML_NEW = (
    "  var _evs=d.evidences&&d.evidences.length>0?d.evidences:(d.evidence?[{name:d.evidenceName||'File',data:d.evidence}]:[]);\n"
    "  _viewEvs(_evs);"
)

# Compact single-line modal block (d.evidence)
MODAL_D_CL = (
    "document.getElementById('sem-name').textContent=d.evidenceName||'Bukti';"
    "var img=document.getElementById('sem-img');"
    "if(d.evidence.startsWith('data:image')){img.src=d.evidence;img.style.display='block';}else{img.style.display='none';}"
    "document.getElementById('store-ev-modal').style.display='flex';"
)
MODAL_D_CL_NEW = (
    "var _evs=d.evidences&&d.evidences.length>0?d.evidences:(d.evidence?[{name:d.evidenceName||'File',data:d.evidence}]:[]);"
    "_viewEvs(_evs);"
)

# Compact single-line modal block (row.evidence)
MODAL_ROW_CL = (
    "document.getElementById('sem-name').textContent=row.evidenceName||'Bukti';"
    "var img=document.getElementById('sem-img');"
    "if(row.evidence.startsWith('data:image')){img.src=row.evidence;img.style.display='block';}else{img.style.display='none';}"
    "document.getElementById('store-ev-modal').style.display='flex';"
)
MODAL_ROW_CL_NEW = (
    "var _evs=row.evidences&&row.evidences.length>0?row.evidences:(row.evidence?[{name:row.evidenceName||'File',data:row.evidence}]:[]);"
    "_viewEvs(_evs);"
)

# Local ev variable modal block (for rot/kdk/IA functions) - multi-line
MODAL_EV_ML = (
    "  document.getElementById('sem-name').textContent=evName||'Bukti';\n"
    "  var img=document.getElementById('sem-img');\n"
    "  if(ev.startsWith('data:image')){img.src=ev;img.style.display='block';}else{img.style.display='none';}\n"
    "  document.getElementById('store-ev-modal').style.display='flex';"
)
MODAL_EV_ML_NEW = "  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);"

# For finaccRotViewEv (evName without ||'Bukti')
MODAL_EV_ML2 = (
    "  document.getElementById('sem-name').textContent=evName;\n"
    "  var img=document.getElementById('sem-img');\n"
    "  if(ev.startsWith('data:image')){img.src=ev;img.style.display='block';}else{img.style.display='none';}\n"
    "  document.getElementById('store-ev-modal').style.display='flex';"
)
MODAL_EV_ML2_NEW = "  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);"

# IA functions (no evName variable, no sem-name update)
MODAL_IA = (
    "  var img=document.getElementById('sem-img');\n"
    "  if(ev.startsWith('data:image')){img.src=ev;img.style.display='block';}else{img.style.display='none';}\n"
    "  document.getElementById('store-ev-modal').style.display='flex';"
)
MODAL_IA_NEW = (
    "  var _evs=data.rows[i].evidences&&data.rows[i].evidences.length>0\n"
    "    ?data.rows[i].evidences:(ev?[{name:data.rows[i].evidenceName||'Bukti',data:ev}]:[]);\n"
    "  _viewEvs(_evs);"
)

# For invRotViewEv and hrdKdkViewEv - use local ev
MODAL_EV_SIMPLE = (
    "  var img=document.getElementById('sem-img');\n"
    "  if(ev.startsWith('data:image')){img.src=ev;img.style.display='block';}else{img.style.display='none';}\n"
    "  document.getElementById('store-ev-modal').style.display='flex';"
)
# Note: same as MODAL_IA but with different replacement
MODAL_EV_SIMPLE_NEW = "  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);"

# storeViewEv has a different notify text: 'Tidak ada bukti tersimpan.'
STORE_EV_CHECK = "if(!d.evidence){notify('Tidak ada bukti tersimpan.','error');return;}"

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []
    patches_ok = []

    # ─── 1. Insert _viewEvs after _evView function ───
    ev_view_marker = "\nwindow._evStore={};\n"
    if ev_view_marker in c:
        c = c.replace(ev_view_marker, "\nwindow._evStore={};\n" + VIEW_EVS, 1)
        patches_ok.append('1: _viewEvs added')
    else:
        errors.append('1: _evStore marker not found')

    # ─── 2. Multi-line d.evidence modal → _viewEvs ───
    cnt = c.count(MODAL_D_ML)
    c = c.replace(MODAL_D_ML, MODAL_D_ML_NEW)
    patches_ok.append(f'2: {cnt} multi-line d.evidence modal replaced')

    # ─── 3. Compact d.evidence modal → _viewEvs ───
    cnt = c.count(MODAL_D_CL)
    c = c.replace(MODAL_D_CL, MODAL_D_CL_NEW)
    patches_ok.append(f'3: {cnt} compact d.evidence modal replaced')

    # ─── 4. Compact row.evidence modal → _viewEvs ───
    cnt = c.count(MODAL_ROW_CL)
    c = c.replace(MODAL_ROW_CL, MODAL_ROW_CL_NEW)
    patches_ok.append(f'4: {cnt} compact row.evidence modal replaced')

    # ─── 5. finaccRotViewEv / gaRotViewEv (evName without fallback) ───
    cnt = c.count(MODAL_EV_ML2)
    c = c.replace(MODAL_EV_ML2, MODAL_EV_ML2_NEW)
    patches_ok.append(f'5: {cnt} evName (no fallback) modal replaced')

    # ─── 6. hrdKdkViewEv / invRotViewEv (evName with fallback) ───
    # These have sem-name update
    cnt = c.count(MODAL_EV_ML)
    c = c.replace(MODAL_EV_ML, MODAL_EV_ML_NEW)
    patches_ok.append(f'6: {cnt} ev/evName modal replaced')

    # ─── 7. IA functions (iaRekoViewEvidence, iaRotViewEvidence, iaProjViewEvidence) ───
    # These have ev from data.rows[i].evidence, and evidences from data.rows[i].evidences
    # But: iaRekoViewEvidence, iaRotViewEvidence, iaProjViewEvidence all use same pattern:
    # "  var img=document.getElementById('sem-img');\n  if(ev.startsWith..."
    # We already handled invRotViewEv/hrdKdkViewEv above (they have sem-name before img)
    # IA functions don't update sem-name, so their pattern is different
    ia_old = (
        "  var img=document.getElementById('sem-img');\n"
        "  if(ev.startsWith('data:image')){img.src=ev;img.style.display='block';}else{img.style.display='none';}\n"
        "  document.getElementById('store-ev-modal').style.display='flex';"
    )
    ia_new = (
        "  var _evs=data.rows[i].evidences&&data.rows[i].evidences.length>0\n"
        "    ?data.rows[i].evidences:(ev?[{name:data.rows[i].evidenceName||'Bukti',data:ev}]:[]);\n"
        "  _viewEvs(_evs);"
    )
    cnt = c.count(ia_old)
    c = c.replace(ia_old, ia_new)
    patches_ok.append(f'7: {cnt} IA ev modal replaced')

    # ─── 8. Fix invRotViewEv / finaccRotViewEv: use akurasiEvs/ontimeEvs arrays ───
    # invRotViewEv uses rot.ontimeEv and rot.akurasiEv - update to use evs arrays
    inv_rot_old = (
        "function invRotViewEv(poinIdx,isOntime){\n"
        "  var rot=_irotg(inventoryYear,invRotMonth);\n"
        "  var ev=isOntime?rot.ontimeEv:(poinIdx===-1?rot.akurasiEv:(rot.poinEv&&rot.poinEv[poinIdx]?rot.poinEv[poinIdx]:null));\n"
        "  var evName=isOntime?rot.ontimeEvName:(poinIdx===-1?(rot.akurasiEvName||'Bukti Temuan'):(rot.poinEvName&&rot.poinEvName[poinIdx]?rot.poinEvName[poinIdx]:'Bukti'));\n"
        "  if(!ev){notify('Tidak ada bukti.','error');return;}\n"
        "  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);\n"
        "}"
    )
    inv_rot_new = (
        "function invRotViewEv(poinIdx,isOntime){\n"
        "  var rot=_irotg(inventoryYear,invRotMonth);\n"
        "  var evs;\n"
        "  if(isOntime){\n"
        "    evs=rot.ontimeEvs&&rot.ontimeEvs.length>0?rot.ontimeEvs:(rot.ontimeEv?[{name:rot.ontimeEvName||'Bukti Ontime',data:rot.ontimeEv}]:[]);\n"
        "  }else if(poinIdx===-1){\n"
        "    evs=rot.akurasiEvs&&rot.akurasiEvs.length>0?rot.akurasiEvs:(rot.akurasiEv?[{name:rot.akurasiEvName||'Bukti Temuan',data:rot.akurasiEv}]:[]);\n"
        "  }else{\n"
        "    var _e=rot.poinEv&&rot.poinEv[poinIdx]?rot.poinEv[poinIdx]:null;\n"
        "    evs=_e?[{name:rot.poinEvName&&rot.poinEvName[poinIdx]?rot.poinEvName[poinIdx]:'Bukti',data:_e}]:[];\n"
        "  }\n"
        "  _viewEvs(evs);\n"
        "}"
    )
    if inv_rot_old in c:
        c = c.replace(inv_rot_old, inv_rot_new, 1)
        patches_ok.append('8a: invRotViewEv updated to use evs arrays')
    else:
        errors.append('8a: invRotViewEv not found (may already be updated)')

    # finaccRotViewEv
    fa_rot_old = (
        "function finaccRotViewEv(type){\n"
        "  var rot=_farotg(finaccYear,finaccReportMonth);\n"
        "  var ev=type==='ontime'?rot.ontimeEv:rot.akurasiEv;\n"
        "  var evName=type==='ontime'?(rot.ontimeEvName||'Bukti Ontime'):(rot.akurasiEvName||'Bukti Akurasi');\n"
        "  if(!ev){notify('Tidak ada bukti.','error');return;}\n"
        "  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);\n"
        "}"
    )
    fa_rot_new = (
        "function finaccRotViewEv(type){\n"
        "  var rot=_farotg(finaccYear,finaccReportMonth);\n"
        "  var evs;\n"
        "  if(type==='ontime'){\n"
        "    evs=rot.ontimeEvs&&rot.ontimeEvs.length>0?rot.ontimeEvs:(rot.ontimeEv?[{name:rot.ontimeEvName||'Bukti Ontime',data:rot.ontimeEv}]:[]);\n"
        "  }else{\n"
        "    evs=rot.akurasiEvs&&rot.akurasiEvs.length>0?rot.akurasiEvs:(rot.akurasiEv?[{name:rot.akurasiEvName||'Bukti Akurasi',data:rot.akurasiEv}]:[]);\n"
        "  }\n"
        "  _viewEvs(evs);\n"
        "}"
    )
    if fa_rot_old in c:
        c = c.replace(fa_rot_old, fa_rot_new, 1)
        patches_ok.append('8b: finaccRotViewEv updated to use evs arrays')
    else:
        errors.append('8b: finaccRotViewEv not found')

    # gaRotViewEv
    ga_rot_old = (
        "function gaRotViewEv(isOntime){\n"
        "  var rot=_garotg(gaYear,gaRotMonth);\n"
        "  var ev=isOntime?rot.ontimeEv:rot.akurasiEv;\n"
        "  var evName=isOntime?(rot.ontimeEvName||'Bukti Ontime'):(rot.akurasiEvName||'Bukti Temuan');\n"
        "  if(!ev){notify('Tidak ada bukti.','error');return;}\n"
        "  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);\n"
        "}"
    )
    ga_rot_new = (
        "function gaRotViewEv(isOntime){\n"
        "  var rot=_garotg(gaYear,gaRotMonth);\n"
        "  var evs;\n"
        "  if(isOntime){\n"
        "    evs=rot.ontimeEvs&&rot.ontimeEvs.length>0?rot.ontimeEvs:(rot.ontimeEv?[{name:rot.ontimeEvName||'Bukti Ontime',data:rot.ontimeEv}]:[]);\n"
        "  }else{\n"
        "    evs=rot.akurasiEvs&&rot.akurasiEvs.length>0?rot.akurasiEvs:(rot.akurasiEv?[{name:rot.akurasiEvName||'Bukti Temuan',data:rot.akurasiEv}]:[]);\n"
        "  }\n"
        "  _viewEvs(evs);\n"
        "}"
    )
    if ga_rot_old in c:
        c = c.replace(ga_rot_old, ga_rot_new, 1)
        patches_ok.append('8c: gaRotViewEv updated to use evs arrays')
    else:
        errors.append('8c: gaRotViewEv not found')

    # ─── Print results ───
    name = fpath.split('\\')[-1]
    sys.stdout.buffer.write(('\n=== ' + name + ' ===\n').encode('utf-8'))
    for p in patches_ok:
        sys.stdout.buffer.write(('  OK: ' + p + '\n').encode('utf-8'))
    if errors:
        sys.stdout.buffer.write('  ERRORS:\n'.encode('utf-8'))
        for e in errors:
            sys.stdout.buffer.write(('  !! ' + e + '\n').encode('utf-8'))

    if not errors:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        sys.stdout.buffer.write(('  Saved: ' + str(len(c)) + ' chars\n').encode('utf-8'))
    else:
        sys.stdout.buffer.write('  NOT SAVED\n'.encode('utf-8'))
