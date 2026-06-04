# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

EXACT = [
    # ===== #2: iaInit selalu reset ke bulan berjalan =====
    ('function iaInit(){\n  var msel=document.getElementById(\'ia-month-sel\');',
     'function iaInit(){\n  _iaCurMonth=new Date().getMonth()+1;\n  _iaCurYear=new Date().getFullYear();\n  var msel=document.getElementById(\'ia-month-sel\');',
     '#2 iaInit reset'),

    # ===== #2: iaShowSub selalu reset ke bulan berjalan + update dropdown =====
    ('''function iaShowSub(sub,btn){
  _iaCurSub=sub;
  document.querySelectorAll('#panel-ia .store-tab').forEach(function(b){b.classList.remove('active');});
  if(btn) btn.classList.add('active');
  iaRefresh();
}''',
     '''function iaShowSub(sub,btn){
  _iaCurSub=sub;
  _iaCurMonth=new Date().getMonth()+1;
  _iaCurYear=new Date().getFullYear();
  var _ms=document.getElementById('ia-month-sel');if(_ms)_ms.value=_iaCurMonth;
  var _ys=document.getElementById('ia-year-sel');if(_ys)_ys.value=_iaCurYear;
  document.querySelectorAll('#panel-ia .store-tab').forEach(function(b){b.classList.remove('active');});
  if(btn) btn.classList.add('active');
  iaRefresh();
}''',
     '#2 iaShowSub reset'),

    # ===== #1: reko Aksi cell + delete button =====
    ('''    h+='</td><td style="padding:8px 10px;text-align:center;">';
    if(locked){h+='<button onclick="iaRekoEdit('+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:12px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';}
    else{h+='<button onclick="iaRekoSaveRow('+i+')" style="background:var(--primary);border:none;color:#fff;padding:5px 14px;border-radius:var(--radius-sm);cursor:pointer;font-size:12px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';}
    h+='</td></tr>';''',
     '''    h+='</td><td style="padding:8px 10px;text-align:center;"><div style="display:flex;gap:6px;justify-content:center;align-items:center;">';
    if(locked){h+='<button onclick="iaRekoEdit('+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:12px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';}
    else{h+='<button onclick="iaRekoSaveRow('+i+')" style="background:var(--primary);border:none;color:#fff;padding:5px 14px;border-radius:var(--radius-sm);cursor:pointer;font-size:12px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';}
    h+='<button onclick="iaRekoDelete('+i+')" style="background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:4px 9px;cursor:pointer;font-size:13px;font-family:var(--font);" title="Hapus data">&#x1F5D1;</button>';
    h+='</div></td></tr>';''',
     '#1 reko aksi+delete btn'),

    # ===== #1: reko delete function (sisipkan sebelum iaRekoViewEvidence) =====
    ('function iaRekoViewEvidence(i){',
     '''function iaRekoDelete(i){
  if(!confirm('Hapus data baris ini?'))return;
  var data=iaRekoLoad(_iaCurYear,_iaCurMonth);
  data.rows[i].score='';data.rows[i].evidence='';data.rows[i].evidenceName='';data.rows[i].evidences=[];data.rows[i].locked=false;
  iaRekoSave(_iaCurYear,_iaCurMonth,data); iaRekoRender(); notify('Data dihapus.');
}
function iaRekoViewEvidence(i){''',
     '#1 iaRekoDelete fn'),

    # ===== #1: rot Aksi cell + delete button =====
    ('''    h+='</td><td style="padding:7px 8px;text-align:center;">';
    if(locked){h+='<button onclick="iaRotEdit(\\''+_iaRotCurType+'\\','+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:11px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';}
    else{h+='<button onclick="iaRotSaveRow(\\''+_iaRotCurType+'\\','+i+')" style="background:var(--primary);border:none;color:#fff;padding:5px 12px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';}
    h+='</td></tr>';''',
     '''    h+='</td><td style="padding:7px 8px;text-align:center;"><div style="display:flex;gap:6px;justify-content:center;align-items:center;">';
    if(locked){h+='<button onclick="iaRotEdit(\\''+_iaRotCurType+'\\','+i+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:11px;font-family:var(--font);" title="Edit">&#x270F;&#xFE0F; Edit</button>';}
    else{h+='<button onclick="iaRotSaveRow(\\''+_iaRotCurType+'\\','+i+')" style="background:var(--primary);border:none;color:#fff;padding:5px 12px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';}
    h+='<button onclick="iaRotDelete(\\''+_iaRotCurType+'\\','+i+')" style="background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:4px 9px;cursor:pointer;font-size:12px;font-family:var(--font);" title="Hapus data">&#x1F5D1;</button>';
    h+='</div></td></tr>';''',
     '#1 rot aksi+delete btn'),

    # ===== #1: rot delete function (sisipkan sebelum iaRotViewEvidence) =====
    ('function iaRotViewEvidence(typeKey,i){',
     '''function iaRotDelete(typeKey,i){
  if(!confirm('Hapus data baris ini?'))return;
  var data=iaRotLoad(typeKey,_iaCurYear,_iaCurMonth);
  data.rows[i].submittedDate='';data.rows[i].temuan='';data.rows[i].evidence='';data.rows[i].evidenceName='';data.rows[i].evidences=[];data.rows[i].locked=false;
  iaRotSave(typeKey,_iaCurYear,_iaCurMonth,data); iaRotRender(); notify('Data dihapus.');
}
function iaRotViewEvidence(typeKey,i){''',
     '#1 iaRotDelete fn'),

    # ===== #3: sync IA Project -> OKR di okrRender (nilai = jumlah project) =====
    ('''  var _RD = (typeof OKR_DIVISI!=='undefined'&&Array.isArray(OKR_DIVISI))''',
     '''  // Sync Internal Audit Project -> OKR "inisiatif proaktif" (nilai = jumlah project locked)
  if(typeof iaProjLoad==='function'&&typeof iaSyncOKR==='function'){
    var _iapRows=(iaProjLoad(okrCurYear,okrCurMonth).rows)||[];
    iaSyncOKR(/inisiatif.*proaktif|proaktif/i,okrCurYear,okrCurMonth,_iapRows.filter(function(r){return r.locked;}).length);
  }
  var _RD = (typeof OKR_DIVISI!=='undefined'&&Array.isArray(OKR_DIVISI))''',
     '#3 okrRender IA project sync'),
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()
    ok=[]; bad=[]
    for old,new,label in EXACT:
        if old in c:
            c=c.replace(old,new,1); ok.append(label)
        else:
            bad.append(label)
    # ===== #4: global 1MB -> 500KB (size check + message) =====
    n1=c.count('f.size>1024*1024')
    c=c.replace('f.size>1024*1024','f.size>500*1024')
    n2=c.count('Ukuran file maksimal 1 MB per file.')
    c=c.replace('Ukuran file maksimal 1 MB per file.','Ukuran file maksimal 500 KB per file.')
    ok.append('#4 size check x%d, message x%d -> 500KB'%(n1,n2))

    name='templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' ===')
    for p in ok: print('  OK: '+p)
    for b in bad: print('  MISSING: '+b)
    if not bad:
        with open(fpath,'w',encoding='utf-8') as f: f.write(c)
        print('  Saved: %d chars'%len(c))
    else:
        print('  NOT saved (%d missing)'%len(bad))
