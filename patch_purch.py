# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

PATCHES = [
    # ===== BUG 1: definisikan ACC_KW (hilang saat rebuild) =====
    ('function purchApoSave(month){\n  var y=purchasingYear;var d=_pgApo(y,month);',
     "var ACC_KW=['HPP','SUPPLIER','HARGA','KUANTITI','QTY','SALAH','DISKON','LEBIH','KURANG','TEMPO','TERMIN','NAMA'];\nfunction purchApoSave(month){\n  var y=purchasingYear;var d=_pgApo(y,month);",
     'BUG1 ACC_KW defined'),

    # ===== BUG 2a: akumulasi In Stock di render — hitung hari yang punya score (file opsional) =====
    ('for(var dd=1;dd<=daysInM;dd++){var dt=new Date(y,m-1,dd);if(dt.getDay()===0)continue;totalWD++;var dd_=_pgIns(y,m,dd);if(dd_.locked&&dd_.file1&&dd_.file2){savedD++;if(dd_.score!==null&&dd_.score!==undefined){scoreSum+=dd_.score;scoreDays++;}}}',
     'for(var dd=1;dd<=daysInM;dd++){var dt=new Date(y,m-1,dd);if(dt.getDay()===0)continue;totalWD++;var dd_=_pgIns(y,m,dd);if(dd_.locked&&dd_.score!==null&&dd_.score!==undefined){savedD++;scoreSum+=dd_.score;scoreDays++;}}',
     'BUG2a render accumulation'),

    # ===== BUG 2b: akumulasi In Stock di sync OKR =====
    ('for(var dd=1;dd<=daysInM;dd++){var dt=new Date(year,month-1,dd);if(dt.getDay()===0)continue;var d=_pgIns(year,month,dd);if(d.locked&&d.file1&&d.file2&&d.score!==null&&d.score!==undefined){scoreSum+=d.score;scoreDays++;}}',
     'for(var dd=1;dd<=daysInM;dd++){var dt=new Date(year,month-1,dd);if(dt.getDay()===0)continue;var d=_pgIns(year,month,dd);if(d.locked&&d.score!==null&&d.score!==undefined){scoreSum+=d.score;scoreDays++;}}',
     'BUG2b sync accumulation'),

    # ===== BUG 2c: tombol Simpan In Stock selalu aktif (boleh simpan score manual tanpa file) =====
    ('''      var canSave=!!(d.file1&&d.file2);
      html+='<td style="text-align:center;"><button onclick="purchInstockConfirmSave('+dd+')"''',
     '''      var canSave=true;
      html+='<td style="text-align:center;"><button onclick="purchInstockConfirmSave('+dd+')"''',
     'BUG2c canSave instock'),

    # ===== BUG 2d: confirmSave In Stock — boleh simpan jika ada score ATAU kedua file =====
    ('''  var d=_pgIns(y,m,day);
  if(!d.file1||!d.file2){notify('Upload kedua file terlebih dahulu','error');return;}
  var scEl=document.getElementById('pins-sc-'+day);
  var sc=scEl&&scEl.value!==''?parseFloat(scEl.value):null;
  if(sc!==null&&(isNaN(sc)||sc<0||sc>100)){notify('Score harus antara 0 dan 100','error');return;}''',
     '''  var d=_pgIns(y,m,day);
  var scEl=document.getElementById('pins-sc-'+day);
  var sc=scEl&&scEl.value!==''?parseFloat(scEl.value):null;
  if(sc===null&&(!d.file1||!d.file2)){notify('Isi Score atau upload kedua file terlebih dahulu','error');return;}
  if(sc!==null&&(isNaN(sc)||sc<0||sc>100)){notify('Score harus antara 0 dan 100','error');return;}''',
     'BUG2d confirmSave instock'),

    # ===== BUG 2e: teks modal konfirmasi In Stock =====
    ("document.getElementById('pc-val').textContent='File 1 + File 2 siap disimpan';",
     "document.getElementById('pc-val').textContent=(sc!==null?'Score: '+sc+'%':'Data')+' siap disimpan';",
     'BUG2e modal text'),
]

for fpath in files:
    with open(fpath,'r',encoding='utf-8') as f: c=f.read()
    ok=[];bad=[]
    for old,new,label in PATCHES:
        if old in c: c=c.replace(old,new,1); ok.append(label)
        else: bad.append(label)
    name='templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' ===')
    for p in ok: print('  OK: '+p)
    for b in bad: print('  MISSING: '+b)
    if not bad:
        with open(fpath,'w',encoding='utf-8') as f: f.write(c)
        print('  Saved: %d chars'%len(c))
    else:
        print('  NOT saved (%d missing)'%len(bad))
