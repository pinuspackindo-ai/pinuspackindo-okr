# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

# helper: append bukti baru ke yang sudah ada, maksimal 3 total
HELPER = 'function _apEv(ex,inc){var b=(ex&&ex.length)?ex.slice():[];var o=b.concat(inc||[]);return o.length>3?o.slice(0,3):o;}\n'

# (old, new, replace_all?) — None artinya replace semua kemunculan
REPL = [
    # sisipkan helper sebelum window._evStore={}
    ('window._evStore={};', HELPER+'window._evStore={};', False),

    # ---- evidence storage: ubah REPLACE -> APPEND (maks 3) ----
    ('d.evidences=results', 'd.evidences=_apEv(d.evidences,results)', True),
    ('d.evidences=_evs||[]', 'd.evidences=_apEv(d.evidences,_evs)', True),
    ('rot.akurasiEvs=_evs||[]', 'rot.akurasiEvs=_apEv(rot.akurasiEvs,_evs)', True),
    ('rot.ontimeEvs=_evs||[]', 'rot.ontimeEvs=_apEv(rot.ontimeEvs,_evs)', True),
    ('row.evidences=_evs||[]', 'row.evidences=_apEv(row.evidences,_evs)', True),
    ('data.rows[i].evidences=results', 'data.rows[i].evidences=_apEv(data.rows[i].evidences,results)', True),

    # ---- tombol Simpan IA: samakan kecil + nowrap (cegah teks wrapping) ----
    # reko
    ('<button onclick="iaRekoSaveRow(\'+i+\')" style="background:var(--primary);border:none;color:#fff;padding:5px 14px;border-radius:var(--radius-sm);cursor:pointer;font-size:12px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>',
     '<button onclick="iaRekoSaveRow(\'+i+\')" style="background:var(--primary);border:none;color:#fff;padding:4px 10px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;white-space:nowrap;">&#x1F4BE; Simpan</button>',
     False),
    # rot
    ('<button onclick="iaRotSaveRow(\\\'\'+_iaRotCurType+\'\\\',\'+i+\')" style="background:var(--primary);border:none;color:#fff;padding:5px 12px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>',
     '<button onclick="iaRotSaveRow(\\\'\'+_iaRotCurType+\'\\\',\'+i+\')" style="background:var(--primary);border:none;color:#fff;padding:4px 10px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;white-space:nowrap;">&#x1F4BE; Simpan</button>',
     False),
    # proj
    ('<button onclick="iaProjSaveRow(\'+i+\')" style="background:var(--primary);border:none;color:#fff;padding:6px 16px;border-radius:var(--radius-sm);cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>',
     '<button onclick="iaProjSaveRow(\'+i+\')" style="background:var(--primary);border:none;color:#fff;padding:4px 10px;border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;white-space:nowrap;">&#x1F4BE; Simpan</button>',
     False),
]

for fpath in files:
    with open(fpath,'r',encoding='utf-8') as f: c=f.read()
    ok=[];bad=[]
    for old,new,allf in REPL:
        n=c.count(old)
        if n>0:
            c=c.replace(old,new) if allf else c.replace(old,new,1)
            ok.append('(%dx) %s'%(n if allf else 1, old[:45]))
        else:
            bad.append(old[:55])
    name='templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' ===')
    for p in ok: print('  OK',p)
    for b in bad: print('  MISSING:',b)
    if not bad:
        with open(fpath,'w',encoding='utf-8') as f: f.write(c)
        print('  Saved',len(c))
    else: print('  NOT saved')
