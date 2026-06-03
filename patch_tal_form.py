files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

# ═══════════════════════════════════════════════════════════════
# NEW FORM SECTION in talRender() — multi-item, no Target/Progress
# ═══════════════════════════════════════════════════════════════
OLD_FORM = (
    "  html+='<div id=\"tal-add-form\" style=\"display:none;background:var(--bg2);border:1.5px solid var(--primary);border-radius:var(--radius);padding:20px;margin-bottom:20px;\">';\n"
    "  html+='<div style=\"font-size:14px;font-weight:700;color:var(--text);margin-bottom:14px;\">&#x1F4CB; Tambah TAL Baru</div>';\n"
    "  html+='<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:12px;\">';\n"
    "  html+='<div><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Nama Divisi</label><select id=\"tal-form-div\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\">'+divOpts+'</select></div>';\n"
    "  html+='<div style=\"grid-column:span 2;\"><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Deskripsi TAL</label><input type=\"text\" id=\"tal-form-tal\" placeholder=\"Deskripsi TAL...\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\"></div>';\n"
    "  html+='<div><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Deadline</label><input type=\"date\" id=\"tal-form-dl\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\"></div>';\n"
    "  html+='<div><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Target</label><input type=\"text\" id=\"tal-form-tgt\" placeholder=\"Target...\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\"></div>';\n"
    "  html+='<div><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Bobot (%)</label><input type=\"number\" id=\"tal-form-bbt\" min=\"0.01\" max=\"100\" step=\"0.01\" placeholder=\"%\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\"></div>';\n"
    "  html+='<div><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Progress (%)</label><input type=\"number\" id=\"tal-form-prg\" min=\"0\" max=\"100\" step=\"0.01\" placeholder=\"%\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\"></div>';\n"
    "  html+='</div>';\n"
    "  html+='<div style=\"margin-bottom:12px;\"><label style=\"font-size:11px;color:var(--text-m);font-weight:600;\">Review Atasan</label><input type=\"text\" id=\"tal-form-rvw\" placeholder=\"Review atasan...\" style=\"width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;\"></div>';\n"
    "  html+='<div style=\"display:flex;gap:8px;\">';\n"
    "  html+='<button onclick=\"talFormSave()\" style=\"background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 20px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;\">&#x2713; Simpan</button>';\n"
    "  html+='<button onclick=\"talFormCancel()\" style=\"background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:7px 14px;cursor:pointer;font-size:13px;font-family:var(--font);\">&#x2715; Batal</button>';\n"
    "  html+='</div></div>';"
)

NEW_FORM = (
    "  html+='<div id=\"tal-add-form\" style=\"display:none;background:var(--bg2);border:1.5px solid var(--primary);border-radius:var(--radius);padding:20px;margin-bottom:20px;\">';\n"
    "  html+='<div style=\"font-size:14px;font-weight:700;color:var(--text);margin-bottom:14px;\">&#x1F4CB; Tambah TAL Baru</div>';\n"
    "  html+='<div style=\"margin-bottom:14px;\"><label style=\"font-size:11px;color:var(--text-m);font-weight:600;display:block;margin-bottom:4px;\">Nama Divisi</label>';\n"
    "  html+='<select id=\"tal-form-div\" style=\"padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;min-width:200px;\">'+divOpts+'</select></div>';\n"
    "  html+='<div style=\"font-size:11px;font-weight:600;color:var(--text-m);margin-bottom:8px;border-top:1px solid var(--border);padding-top:12px;\">Daftar TAL</div>';\n"
    "  html+='<div id=\"tal-form-items\">'+talFormItemHTML(0)+'</div>';\n"
    "  html+='<button onclick=\"talFormAddItem()\" style=\"background:none;border:1.5px dashed var(--primary);color:var(--primary);border-radius:var(--radius-sm);padding:6px 16px;cursor:pointer;font-size:12px;font-family:var(--font);margin-top:4px;\">&#x2795; Tambah Baris TAL</button>';\n"
    "  html+='<div style=\"display:flex;gap:8px;margin-top:14px;border-top:1px solid var(--border);padding-top:12px;\">';\n"
    "  html+='<button onclick=\"talFormSave()\" style=\"background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 20px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;\">&#x2713; Simpan</button>';\n"
    "  html+='<button onclick=\"talFormCancel()\" style=\"background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:7px 14px;cursor:pointer;font-size:13px;font-family:var(--font);\">&#x2715; Batal</button>';\n"
    "  html+='</div></div>';"
)

# ── TABLE HEADER: remove Target ──────────────────────────────
OLD_HDR = "  var hdrs=['No','TAL','Deadline','Target','Progress (%)','Bobot (%)','Score','Review Atasan'];"
NEW_HDR = "  var hdrs=['No','TAL','Deadline','Progress (%)','Bobot (%)','Score','Review Atasan'];"

# ── EDIT ROW: remove target input ────────────────────────────
OLD_EDIT_TGT = "      h+='<td style=\"padding:5px 6px;min-width:110px;\"><input id=\"tal-tgt-'+d+'-'+idx+'\" type=\"text\" value=\"'+okrEsc(row.target||'')+'\" placeholder=\"Target...\" style=\"width:100%;padding:5px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;box-sizing:border-box;\"></td>';"
NEW_EDIT_TGT = ""  # remove entirely

# ── READ-ONLY ROW: remove target cell ────────────────────────
OLD_RO_TGT = "      h+='<td style=\"padding:8px 10px;color:var(--text-m);\">'+okrEsc(row.target||'?')+'</td>';"
NEW_RO_TGT = ""  # remove entirely

# ── FOOTER COLSPAN: 6 -> 5 (one fewer column) ────────────────
OLD_FOOTER_CS = "  h+='<td colspan=\"6\" style=\"padding:11px 14px;font-weight:700;font-size:13px;color:var(--text);text-align:right;\">&#x1F3AF; Score Akhir &nbsp;=&nbsp; &#x2211; (Progress &times; Bobot / 100)</td>';"
NEW_FOOTER_CS = "  h+='<td colspan=\"5\" style=\"padding:11px 14px;font-weight:700;font-size:13px;color:var(--text);text-align:right;\">&#x1F3AF; Score Akhir &nbsp;=&nbsp; &#x2211; (Progress &times; Bobot / 100)</td>';"

# ── talOpenAddForm: reset counter ────────────────────────────
OLD_OPEN = (
    "function talOpenAddForm(){\n"
    "  var form=document.getElementById('tal-add-form');\n"
    "  if(form){form.style.display=form.style.display==='none'?'block':'none';if(form.style.display==='block')form.scrollIntoView({behavior:'smooth',block:'start'});}\n"
    "}"
)
NEW_OPEN = (
    "function talOpenAddForm(){\n"
    "  window._talFiCount=0;\n"
    "  var form=document.getElementById('tal-add-form');\n"
    "  if(form){form.style.display=form.style.display==='none'?'block':'none';if(form.style.display==='block')form.scrollIntoView({behavior:'smooth',block:'start'});}\n"
    "}"
)

# ── talFormSave: multi-item, no target, no progress ──────────
OLD_FORM_SAVE = (
    "function talFormSave(){\n"
    "  var divEl=document.getElementById('tal-form-div');\n"
    "  var talEl=document.getElementById('tal-form-tal');\n"
    "  var dlEl=document.getElementById('tal-form-dl');\n"
    "  var tgtEl=document.getElementById('tal-form-tgt');\n"
    "  var bbtEl=document.getElementById('tal-form-bbt');\n"
    "  var prgEl=document.getElementById('tal-form-prg');\n"
    "  var rvwEl=document.getElementById('tal-form-rvw');\n"
    "  if(!divEl||!talEl) return;\n"
    "  var d=parseInt(divEl.value);\n"
    "  var talVal=(talEl.value||'').trim();\n"
    "  if(!talVal){notify('Deskripsi TAL wajib diisi.','error');return;}\n"
    "  var bobot=bbtEl&&bbtEl.value.trim()!==''?parseFloat(bbtEl.value):0;\n"
    "  if(!bobot||bobot<=0){notify('Bobot (%) wajib diisi dan > 0.','error');return;}\n"
    "  var data=_talG(d,talYear,talMonth);\n"
    "  data.rows.push({\n"
    "    tal:talVal,deadline:dlEl?dlEl.value:'',target:(tgtEl?tgtEl.value:'').trim(),\n"
    "    bobot:Math.min(100,Math.max(0.01,bobot)),\n"
    "    progress:prgEl&&prgEl.value.trim()!==''?Math.min(100,Math.max(0,parseFloat(prgEl.value)||0)):null,\n"
    "    review:(rvwEl?rvwEl.value:'').trim(),editing:false,savedAt:new Date().toISOString()\n"
    "  });\n"
    "  _talS(d,talYear,talMonth,data);okrSaveLS();\n"
    "  // clear form\n"
    "  talEl.value='';if(dlEl)dlEl.value='';if(tgtEl)tgtEl.value='';if(bbtEl)bbtEl.value='';if(prgEl)prgEl.value='';if(rvwEl)rvwEl.value='';\n"
    "  talRender();notify('TAL berhasil ditambahkan ✓');\n"
    "}"
)
NEW_FORM_SAVE = (
    "function talFormItemHTML(i){\n"
    "  var INP='padding:6px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;box-sizing:border-box;width:100%;';\n"
    "  var h='<div id=\"tal-fi-wrap-'+i+'\" style=\"display:grid;grid-template-columns:2fr 140px 90px 32px;gap:8px;align-items:flex-end;margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid var(--border);\">';\n"
    "  h+='<div><label style=\"font-size:10px;color:var(--text-m);font-weight:600;display:block;margin-bottom:3px;\">Deskripsi TAL</label><input type=\"text\" id=\"tal-fi-tal-'+i+'\" placeholder=\"Deskripsi TAL...\" style=\"'+INP+'\"></div>';\n"
    "  h+='<div><label style=\"font-size:10px;color:var(--text-m);font-weight:600;display:block;margin-bottom:3px;\">Deadline</label><input type=\"date\" id=\"tal-fi-dl-'+i+'\" style=\"'+INP+'\"></div>';\n"
    "  h+='<div><label style=\"font-size:10px;color:var(--text-m);font-weight:600;display:block;margin-bottom:3px;\">Bobot (%)</label><input type=\"number\" id=\"tal-fi-bbt-'+i+'\" min=\"0.01\" max=\"100\" step=\"0.01\" placeholder=\"%\" style=\"'+INP+'\"></div>';\n"
    "  h+=(i>0?'<button onclick=\"talFormRemoveItem('+i+')\" style=\"background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:5px 7px;cursor:pointer;font-size:13px;line-height:1;\">&#x1F5D1;</button>':'<div></div>');\n"
    "  h+='</div>';\n"
    "  return h;\n"
    "}\n"
    "function talFormAddItem(){\n"
    "  if(!window._talFiCount) window._talFiCount=0;\n"
    "  window._talFiCount++;\n"
    "  var i=window._talFiCount;\n"
    "  var container=document.getElementById('tal-form-items');\n"
    "  if(!container) return;\n"
    "  var tmp=document.createElement('div');\n"
    "  tmp.innerHTML=talFormItemHTML(i);\n"
    "  container.appendChild(tmp.firstChild);\n"
    "}\n"
    "function talFormRemoveItem(i){\n"
    "  var wrap=document.getElementById('tal-fi-wrap-'+i);\n"
    "  if(wrap) wrap.remove();\n"
    "}\n"
    "function talFormSave(){\n"
    "  var divEl=document.getElementById('tal-form-div');\n"
    "  if(!divEl) return;\n"
    "  var d=parseInt(divEl.value);\n"
    "  var container=document.getElementById('tal-form-items');\n"
    "  if(!container) return;\n"
    "  var items=[];\n"
    "  var talEls=container.querySelectorAll('[id^=\"tal-fi-tal-\"]');\n"
    "  talEls.forEach(function(talEl){\n"
    "    var idx=talEl.id.replace('tal-fi-tal-','');\n"
    "    var talVal=(talEl.value||'').trim();\n"
    "    if(!talVal) return;\n"
    "    var dlEl=document.getElementById('tal-fi-dl-'+idx);\n"
    "    var bbtEl=document.getElementById('tal-fi-bbt-'+idx);\n"
    "    var bobot=bbtEl&&bbtEl.value.trim()!==''?parseFloat(bbtEl.value):0;\n"
    "    items.push({tal:talVal,deadline:dlEl?dlEl.value:'',bobot:Math.min(100,Math.max(0.01,bobot||0)),progress:null,review:'',editing:false,savedAt:new Date().toISOString()});\n"
    "  });\n"
    "  if(items.length===0){notify('Minimal 1 TAL harus diisi.','error');return;}\n"
    "  var invalid=items.find(function(it){return !it.bobot||it.bobot<=0;});\n"
    "  if(invalid){notify('Bobot (%) wajib diisi dan > 0 untuk setiap TAL.','error');return;}\n"
    "  var data=_talG(d,talYear,talMonth);\n"
    "  items.forEach(function(it){data.rows.push(it);});\n"
    "  _talS(d,talYear,talMonth,data);okrSaveLS();\n"
    "  talRender();notify(items.length+' TAL berhasil ditambahkan ✓');\n"
    "}"
)

# ── talSaveRow: remove target field ──────────────────────────
OLD_SAVE_ROW_TGT = (
    "  var tgEl=document.getElementById('tal-tgt-'+d+'-'+idx);\n"
    "  var pEl=document.getElementById('tal-prg-'+d+'-'+idx);\n"
)
NEW_SAVE_ROW_TGT = "  var pEl=document.getElementById('tal-prg-'+d+'-'+idx);\n"

OLD_SAVE_ROW_APPLY = "  row.tal=tal;row.deadline=dlEl?dlEl.value:'';row.target=(tgEl?tgEl.value:'').trim();"
NEW_SAVE_ROW_APPLY = "  row.tal=tal;row.deadline=dlEl?dlEl.value:'';"

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []
    patches_ok = []

    def patch(old, new, label):
        if old in c:
            return c.replace(old, new, 1), label + ' OK'
        return c, '!! ' + label + ' NOT FOUND'

    def do(old, new, label):
        result, msg = patch(old, new, label)
        if msg.startswith('!!'):
            errors.append(msg)
        else:
            patches_ok.append(msg)
        return result

    c = do(OLD_FORM,          NEW_FORM,          'P1: form -> multi-item')
    c = do(OLD_HDR,           NEW_HDR,           'P2: table header remove Target')
    c = do(OLD_EDIT_TGT,      '',                'P3: edit row remove target input')
    c = do(OLD_RO_TGT,        '',                'P4: read-only row remove target td')
    c = do(OLD_FOOTER_CS,     NEW_FOOTER_CS,     'P5: footer colspan 6->5')
    c = do(OLD_OPEN,          NEW_OPEN,          'P6: talOpenAddForm reset counter')
    c = do(OLD_FORM_SAVE,     NEW_FORM_SAVE,     'P7: talFormSave multi-item')
    c = do(OLD_SAVE_ROW_TGT,  NEW_SAVE_ROW_TGT,  'P8a: talSaveRow remove tgEl')
    c = do(OLD_SAVE_ROW_APPLY,NEW_SAVE_ROW_APPLY,'P8b: talSaveRow remove target apply')

    name = fpath.split('\\')[-1] + ' (' + ('index' if 'templates' not in fpath else 'templates') + ')'
    print(f'\n=== {name} ===')
    for p in patches_ok:
        print(f'  OK: {p}')
    if errors:
        print('  ERRORS:')
        for e in errors:
            print(f'  !! {e}')

    if not errors:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'  Saved: {len(c)} chars')
    else:
        print('  NOT saved')
