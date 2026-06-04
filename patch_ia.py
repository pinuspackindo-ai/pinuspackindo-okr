# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

PATCHES = [
    # ===== #4: IA project score = jumlah project (bukan persentase) =====
    ('iaSyncOKR(/inisiatif.*proaktif|proaktif/i,y,m,count*50);',
     'iaSyncOKR(/inisiatif.*proaktif|proaktif/i,y,m,count);',
     '#4a iaProjSave count'),

    ('  var projScore=lockedCount*50;',
     '  var projScore=lockedCount;',
     '#4b projScore count'),

    ('''  h+='<span style="font-size:13px;color:var(--tx2);">Score OKR: <span class="'+scoreClass(Math.min(100,projScore))+'" style="font-weight:800;font-size:18px;">'+projScore+'%</span></span>';''',
     '''  h+='<span style="font-size:13px;color:var(--tx2);">Score OKR: <strong style="font-weight:800;font-size:18px;color:var(--acc);">'+projScore+'</strong></span>';''',
     '#4c projScore display no %'),

    # ===== #5b: upload tidak reset inputan manual/tanggal =====
    # iaReko: preserve score
    ('''    var data=iaRekoLoad(_iaCurYear,_iaCurMonth);
    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';''',
     '''    var data=iaRekoLoad(_iaCurYear,_iaCurMonth);
    var _scEl=document.getElementById('ia-reko-score-'+i);if(_scEl)data.rows[i].score=_scEl.value.trim();
    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';''',
     '#5b iaRekoUpload preserve score'),

    # iaRot: preserve date + temuan
    ('''    var data=iaRotLoad(typeKey,_iaCurYear,_iaCurMonth);
    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';''',
     '''    var data=iaRotLoad(typeKey,_iaCurYear,_iaCurMonth);
    var _dtEl=document.getElementById('ia-rot-date-'+i);if(_dtEl)data.rows[i].submittedDate=_dtEl.value.trim();
    var _tmEl=document.getElementById('ia-rot-temuan-'+i);if(_tmEl)data.rows[i].temuan=_tmEl.value.trim();
    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';''',
     '#5b iaRotUpload preserve date+temuan'),

    # iaProj: preserve nama + tujuan
    ('''    var data=iaProjLoad(_iaCurYear,_iaCurMonth);
    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';''',
     '''    var data=iaProjLoad(_iaCurYear,_iaCurMonth);
    var _nmEl=document.getElementById('ia-proj-nama-'+i);if(_nmEl)data.rows[i].namaProject=_nmEl.value;
    var _tjEl=document.getElementById('ia-proj-tujuan-'+i);if(_tjEl)data.rows[i].tujuan=_tjEl.value;
    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';''',
     '#5b iaProjUpload preserve nama+tujuan'),

    # ===== #5a: tombol action disamakan dengan modul lain =====
    # iaReko Save
    ('''    else{h+='<button onclick="iaRekoSaveRow('+i+')" style="background:var(--acc);border:none;color:#fff;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:12px;">Simpan</button>';}''',
     '''    else{h+='<button onclick="iaRekoSaveRow('+i+')" style="background:var(--primary);border:none;color:#fff;padding:5px 14px;border-radius:var(--radius-sm);cursor:pointer;font-size:12px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';}''',
     '#5a iaReko save btn'),
    # iaReko Edit
    ('''    if(locked){h+='<button onclick="iaRekoEdit('+i+')" style="background:none;border:none;color:var(--acc);cursor:pointer;font-size:20px;" title="Edit">✏️</button>';}''',
     '''    if(locked){h+='<button onclick="iaRekoEdit('+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:12px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';}''',
     '#5a iaReko edit btn'),

    # iaRot Save
    ('''    else{h+='<button onclick="iaRotSaveRow(\\''+_iaRotCurType+'\\','+i+')" style="background:var(--acc);border:none;color:#fff;padding:3px 10px;border-radius:6px;cursor:pointer;font-size:11px;">Simpan</button>';}''',
     '''    else{h+='<button onclick="iaRotSaveRow(\\''+_iaRotCurType+'\\','+i+')" style="background:var(--primary);border:none;color:#fff;padding:5px 12px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';}''',
     '#5a iaRot save btn'),
    # iaRot Edit
    ('''    if(locked){h+='<button onclick="iaRotEdit(\\''+_iaRotCurType+'\\','+i+')" style="background:none;border:none;color:var(--acc);cursor:pointer;font-size:20px;" title="Edit">✏️</button>';}''',
     '''    if(locked){h+='<button onclick="iaRotEdit(\\''+_iaRotCurType+'\\','+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:11px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';}''',
     '#5a iaRot edit btn'),

    # iaProj Edit
    ('''        h+='<button onclick="iaProjEdit('+i+')" style="background:none;border:none;color:var(--acc);cursor:pointer;font-size:20px;" title="Edit">✏️</button>';''',
     '''        h+='<button onclick="iaProjEdit('+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:12px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';''',
     '#5a iaProj edit btn'),
    # iaProj Delete
    ('''        h+='<button onclick="iaProjDelete('+i+')" style="background:none;border:none;color:#ef4444;cursor:pointer;font-size:20px;" title="Hapus">🗑️</button>';''',
     '''        h+='<button onclick="iaProjDelete('+i+')" style="background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:4px 9px;cursor:pointer;font-size:13px;font-family:var(--font);" title="Hapus">&#x1F5D1;</button>';''',
     '#5a iaProj delete btn'),
    # iaProj Save
    ('''        h+='<button onclick="iaProjSaveRow('+i+')" style="background:var(--acc);border:none;color:#fff;padding:6px 16px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;">Simpan</button>';''',
     '''        h+='<button onclick="iaProjSaveRow('+i+')" style="background:var(--primary);border:none;color:#fff;padding:6px 16px;border-radius:var(--radius-sm);cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';''',
     '#5a iaProj save btn'),
    # iaProj Batal
    ('''        h+='<button onclick="iaProjCancelRow('+i+')" style="background:var(--bg2);border:1px solid var(--brd);color:var(--tx);padding:6px 14px;border-radius:8px;cursor:pointer;font-size:13px;">Batal</button>';''',
     '''        h+='<button onclick="iaProjCancelRow('+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);padding:6px 14px;border-radius:var(--radius-sm);cursor:pointer;font-size:13px;font-family:var(--font);">&#x2715; Batal</button>';''',
     '#5a iaProj batal btn'),
    # iaProj Tambah Project
    ('''  h+='<div style="margin-bottom:16px;"><button onclick="iaProjAddRow()" style="background:var(--acc);border:none;color:#fff;padding:8px 18px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;">➕ Tambah Project</button></div>';''',
     '''  h+='<div style="margin-bottom:16px;"><button onclick="iaProjAddRow()" style="background:var(--primary);border:none;color:#fff;padding:8px 18px;border-radius:var(--radius-sm);cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2795; Tambah Project</button></div>';''',
     '#5a iaProj add btn'),
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()
    ok = []; bad = []
    for old, new, label in PATCHES:
        if old in c:
            c = c.replace(old, new, 1); ok.append(label)
        else:
            bad.append(label)
    name = 'templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' ===')
    for p in ok: print('  OK: '+p)
    for b in bad: print('  MISSING: '+b)
    if not bad:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print('  Saved: %d chars'%len(c))
    else:
        print('  NOT saved (%d missing)'%len(bad))
