# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]
PATCHES = [
    # dropdown login: jangan pernah kosong
    ('    var allUsers=APP_USERS.filter(function(u){return _dis2.indexOf(u)===-1;}).concat(okrData._customUsers||[]);\n    allUsers.forEach(function(u){',
     '    var allUsers=APP_USERS.filter(function(u){return _dis2.indexOf(u)===-1;}).concat(okrData._customUsers||[]);\n    if(allUsers.length===0)allUsers=APP_USERS.slice();\n    allUsers.forEach(function(u){',
     'login dropdown never-empty fallback'),
    # session restore: validUsers jangan pernah kosong
    ('  var validUsers=APP_USERS.filter(function(u){return _disV.indexOf(u)===-1;}).concat(okrData._customUsers||[]);\n  if(u&&validUsers.indexOf(u)>=0){',
     '  var validUsers=APP_USERS.filter(function(u){return _disV.indexOf(u)===-1;}).concat(okrData._customUsers||[]);\n  if(validUsers.length===0)validUsers=APP_USERS.slice();\n  if(u&&validUsers.indexOf(u)>=0){',
     'session restore validUsers fallback'),
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
