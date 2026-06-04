# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]
PATCHES = [
    # render: hitung tiap hari yang punya score (tanpa syarat locked)
    ('for(var dd=1;dd<=daysInM;dd++){var dt=new Date(y,m-1,dd);if(dt.getDay()===0)continue;totalWD++;var dd_=_pgIns(y,m,dd);if(dd_.locked&&dd_.score!==null&&dd_.score!==undefined){savedD++;scoreSum+=dd_.score;scoreDays++;}}',
     'for(var dd=1;dd<=daysInM;dd++){var dt=new Date(y,m-1,dd);if(dt.getDay()===0)continue;totalWD++;var dd_=_pgIns(y,m,dd);if(dd_.score!==null&&dd_.score!==undefined&&dd_.score!==\'\'){savedD++;scoreSum+=parseFloat(dd_.score)||0;scoreDays++;}}',
     'render count-by-score'),
    # sync OKR: idem
    ('for(var dd=1;dd<=daysInM;dd++){var dt=new Date(year,month-1,dd);if(dt.getDay()===0)continue;var d=_pgIns(year,month,dd);if(d.locked&&d.score!==null&&d.score!==undefined){scoreSum+=d.score;scoreDays++;}}',
     'for(var dd=1;dd<=daysInM;dd++){var dt=new Date(year,month-1,dd);if(dt.getDay()===0)continue;var d=_pgIns(year,month,dd);if(d.score!==null&&d.score!==undefined&&d.score!==\'\'){scoreSum+=parseFloat(d.score)||0;scoreDays++;}}',
     'sync count-by-score'),
]
for fpath in files:
    with open(fpath,'r',encoding='utf-8') as f: c=f.read()
    ok=[];bad=[]
    for old,new,label in PATCHES:
        if old in c: c=c.replace(old,new,1); ok.append(label)
        else: bad.append(label)
    name='templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' ===')
    for p in ok: print('  OK:',p)
    for b in bad: print('  MISSING:',b)
    if not bad:
        with open(fpath,'w',encoding='utf-8') as f: f.write(c)
        print('  Saved',len(c),'chars')
    else: print('  NOT saved')
