# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

D_OLD = ("  document.getElementById('sem-name').textContent=d.evidenceName||'Bukti';\n"
         "  var img=document.getElementById('sem-img');\n"
         "  if(d.evidence.startsWith('data:image')){img.src=d.evidence;img.style.display='block';}else{img.style.display='none';}\n"
         "  document.getElementById('store-ev-modal').style.display='flex';")
D_NEW = ("  var _evs=d.evidences&&d.evidences.length>0?d.evidences:(d.evidence?[{name:d.evidenceName||'File',data:d.evidence}]:[]);\n"
         "  _viewEvs(_evs);")

ROW_OLD = ("  document.getElementById('sem-name').textContent=row.evidenceName||'Bukti';\n"
           "  var img=document.getElementById('sem-img');\n"
           "  if(row.evidence.startsWith('data:image')){img.src=row.evidence;img.style.display='block';}else{img.style.display='none';}\n"
           "  document.getElementById('store-ev-modal').style.display='flex';")
ROW_NEW = ("  var _evs=row.evidences&&row.evidences.length>0?row.evidences:(row.evidence?[{name:row.evidenceName||'File',data:row.evidence}]:[]);\n"
           "  _viewEvs(_evs);")

for fpath in files:
    with open(fpath,'r',encoding='utf-8') as f: c=f.read()
    nd=c.count(D_OLD); c=c.replace(D_OLD,D_NEW)
    nr=c.count(ROW_OLD); c=c.replace(ROW_OLD,ROW_NEW)
    c=c.replace('Build: 2026-06-04-v6','Build: 2026-06-05-v7')
    name='templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' === d-block:',nd,'row-block:',nr)
    with open(fpath,'w',encoding='utf-8') as f: f.write(c)
    print('  Saved',len(c))
