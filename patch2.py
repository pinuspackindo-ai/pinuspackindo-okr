import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

for fname in ['index.html','templates/index.html']:
    c = open(fname,encoding='utf-8').read()
    steps=[]

    # ── 4b. OKR Edit/Delete - position-based
    idx_oe=c.find('okrOpenEdit')
    if idx_oe!=-1:
        btn1_start=c.rfind("html+='",0,idx_oe)
        del_end=c.find("html+='</div>';",idx_oe)
        old_btns=c[btn1_start:del_end]
        new_btns='if(isOwnerOrAdmin()){'+old_btns.rstrip()+"}\n    "
        c=c[:btn1_start]+new_btns+c[del_end:]
        steps.append('4b-OKR-edit-del OK')
    else:
        steps.append('4b-OKR-edit-del FAILED')

    # ── 4c. OKR: add visibility check before card HTML
    card_mark='html+=\'<div class="card" style="margin-bottom:16px;padding:0;overflow:hidden;">\';'
    if card_mark in c:
        c=c.replace(card_mark,
            "if(_visDivs!==null&&_visDivs.indexOf(div)===-1) return;\n    "+card_mark, 1)
        steps.append('4c-OKR-visibility OK')
    else:
        steps.append('4c FAILED: '+repr(card_mark[:60]))

    # ── 5a. TAL: remove per-div Duplikat + Tambah TAL from card header
    dup_mark = 'if(rows.length===0){\n    h+=\'<button onclick="talDuplicate(\''
    if dup_mark in c:
        dup_start = c.find(dup_mark)
        tambah_end = c.find("Tambah TAL</button>';", dup_start) + len("Tambah TAL</button>';")
        tambah_end = c.find('\n', tambah_end)+1
        c = c[:dup_start] + c[tambah_end:]
        steps.append('5a-TAL-remove-perdiv-btns OK')
    else:
        steps.append('5a FAILED')

    # ── 5b. TAL row Edit/Delete: Owner+Admin only
    edit_mark = "h+='<button onclick=\"talEditRow('+d+','+idx+')\""
    if edit_mark in c:
        e_start = c.find(edit_mark)
        e_end = c.find("'>&#x1F5D1;</button>';", e_start) + len("'>&#x1F5D1;</button>';")
        old_e = c[e_start:e_end]
        c = c[:e_start] + "if(isOwnerOrAdmin()){" + old_e + "}" + c[e_end:]
        steps.append('5b-TAL-row-editdel-OA OK')
    else:
        steps.append('5b FAILED')

    # ── 5c. TAL: wrap global form in OA check + add Duplikat section
    form_start_mark = '  // Global add form (shown/hidden by button)\n  html+=\'<div id="tal-add-form"'
    if form_start_mark in c:
        fs = c.find(form_start_mark)
        # find closing of form div
        fe_mark = "html+='</div></div>';"
        fe = c.find(fe_mark, fs) + len(fe_mark)
        form_block = c[fs:fe]
        dup_section = (
            "\n  // Duplikat section\n"
            "  html+='<div id=\"tal-dup-section\" style=\"display:none;background:var(--bg2);"
            "border:1.5px solid var(--border);border-radius:var(--radius);"
            "padding:16px;margin-bottom:16px;\">"
            "<div style=\"font-size:13px;font-weight:700;color:var(--text);margin-bottom:10px;\">"
            "&#x1F4CB; Duplikat Bulan Lalu</div>"
            "<div style=\"display:flex;align-items:center;gap:10px;flex-wrap:wrap;\">"
            "<select id=\"tal-dup-div\" style=\"padding:7px 10px;border:1.5px solid var(--border);"
            "border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;\">"
            "'+divOpts+'</select>"
            "<button onclick=\"talDupFromTop()\" style=\"background:var(--primary);border:none;"
            "color:#fff;border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;"
            "font-size:12px;font-family:var(--font);font-weight:600;\">&#x1F4CB; Duplikat</button>"
            "<button onclick=\"document.getElementById(&quot;tal-dup-section&quot;).style.display='none'\" "
            "style=\"background:none;border:1.5px solid var(--border);color:var(--text-m);"
            "border-radius:var(--radius-sm);padding:7px 12px;cursor:pointer;font-size:12px;"
            "font-family:var(--font);\">&#x2715; Batal</button>"
            "</div></div>';"
        )
        top_btns = (
            "  html+='<div style=\"display:flex;gap:8px;margin-bottom:12px;\">"
            "<button onclick=\"talOpenAddForm()\" style=\"background:var(--primary);border:none;"
            "color:#fff;border-radius:var(--radius-sm);padding:8px 18px;cursor:pointer;"
            "font-size:13px;font-family:var(--font);font-weight:600;\">&#x2795; Tambah TAL</button>"
            "<button onclick=\"var ds=document.getElementById('tal-dup-section');"
            "ds.style.display=ds.style.display==='none'?'block':'none'\" "
            "style=\"background:none;border:1.5px solid var(--border);color:var(--text-m);"
            "border-radius:var(--radius-sm);padding:8px 14px;cursor:pointer;font-size:12px;"
            "font-family:var(--font);\">&#x1F4CB; Duplikat Bulan Lalu</button></div>';\n"
        )
        new_block = "  if(isOwnerOrAdmin()){\n" + top_btns + form_block + dup_section + "\n  }\n"
        c = c[:fs] + new_block + c[fe:]
        steps.append('5c-TAL-form-OA-wrap OK')
    else:
        steps.append('5c FAILED')

    # ── 6. Add applyPanelRoleUI before showPanel
    old6="function showPanel(name,btn){"
    new6=(
        "function applyPanelRoleUI(name){\n"
        "  if(name==='dashboard'||name==='tal'||name==='pengaturan') return;\n"
        "  if(isAdminUser()) return;\n"
        "  var panel=document.getElementById('panel-'+name);\n"
        "  if(!panel) return;\n"
        "  panel.querySelectorAll('button').forEach(function(b){\n"
        "    var oc=(b.getAttribute('onclick')||'').toLowerCase();\n"
        "    var txt=b.textContent;\n"
        "    var isEditDel=txt.indexOf('✏')!==-1||txt.indexOf('\U0001f5d1')!==-1||\n"
        "      /\\b(edit|hapus|delete|remove)[a-z]*(row|item|data|fn)?\\s*\\(/.test(oc);\n"
        "    var isSave=/simpan|save|cancel|batal|submit|tutup|close/i.test(txt)||"
        "/simpan|save|cancel|batal/i.test(oc);\n"
        "    if(isEditDel&&!isSave) b.style.display='none';\n"
        "  });\n"
        "}\n"
        "function showPanel(name,btn){"
    )
    if old6 in c:
        c=c.replace(old6,new6,1); steps.append('6-applyPanelRoleUI OK')
    else: steps.append('6 FAILED')

    # ── 7. Call applyPanelRoleUI at end of showPanel
    old7="  if(name==='pengaturan'){pengaturanInit();}\n}"
    new7="  if(name==='pengaturan'){pengaturanInit();}\n  applyPanelRoleUI(name);\n}"
    if old7 in c:
        c=c.replace(old7,new7,1); steps.append('7-showPanel-call OK')
    else: steps.append('7 FAILED')

    # ── 8. Add talDupFromTop function
    old8="function talDuplicate(d){"
    new8=("function talDupFromTop(){\n"
          "  var sel=document.getElementById('tal-dup-div');\n"
          "  if(!sel) return;\n"
          "  talDuplicate(parseInt(sel.value));\n"
          "  document.getElementById('tal-dup-section').style.display='none';\n"
          "}\n"
          "function talDuplicate(d){")
    if old8 in c:
        c=c.replace(old8,new8,1); steps.append('8-talDupFromTop OK')
    else: steps.append('8 FAILED')

    open(fname,'w',encoding='utf-8').write(c)
    for s in steps: print('  '+fname+': '+s)
    print()
