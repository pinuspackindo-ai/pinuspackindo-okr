files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []

    # ─── PATCH 1: Top area - remove Duplikat button + tal-dup-section, keep only Tambah TAL ───
    old1 = (
        '// OA-only: single Tambah TAL + Duplikat top buttons\n'
        '  if(isOwnerOrAdmin()){\n'
        '    html+=\'<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">\';\n'
        '    html+=\'<button onclick="talOpenAddForm()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2795; Tambah TAL</button>\';\n'
        '    html+=\'<button onclick="var s=document.getElementById(\\\'tal-dup-section\\\');s.style.display=s.style.display===\\\'none\\\'?\\\'block\\\':\\\'none\\\';" style="background:none;border:1.5px solid var(--border);color:var(--text);border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);">&#x1F4CB; Duplikat Bulan Lalu</button>\';\n'
        '    html+=\'</div>\';\n'
        '    html+=\'<div id="tal-dup-section" style="display:none;background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:16px;">\';\n'
        '    html+=\'<div style="font-size:13px;font-weight:700;color:var(--text);margin-bottom:10px;">&#x1F4CB; Duplikat dari Bulan Lalu</div>\';\n'
        '    html+=\'<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">\';\n'
        '    html+=\'<label style="font-size:12px;color:var(--text-m);">Divisi:</label>\';\n'
        '    html+=\'<select id="tal-dup-div" style="padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;">\';\n'
        '    divsToShow.forEach(function(idx){ html+=\'<option value="\'+idx+\'">\'+okrEsc(TAL_DIV_NAMES[idx])+\'</option>\'; });\n'
        '    html+=\'</select>\';\n'
        '    html+=\'<button onclick="talDupFromTop()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 14px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x1F4CB; Duplikat</button>\';\n'
        '    html+=\'</div></div>\';\n'
        '  }'
    )
    new1 = (
        '// OA-only: Tambah TAL button at top\n'
        '  if(isOwnerOrAdmin()){\n'
        '    html+=\'<div style="margin-bottom:12px;">\';\n'
        '    html+=\'<button onclick="talOpenAddForm()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2795; Tambah TAL</button>\';\n'
        '    html+=\'</div>\';\n'
        '  }'
    )
    if old1 in c:
        c = c.replace(old1, new1, 1)
        print(fpath.split('\\')[-2]+'/'+fpath.split('\\')[-1], '- PATCH 1 OK')
    else:
        errors.append('PATCH 1 not found')
        print(fpath.split('\\')[-1], '- PATCH 1 MISSING')

    # ─── PATCH 2: Card header - add per-division Duplikat button (OA + rows empty only) ───
    old2 = (
        '  }\n\n'
        '  h+=\'</div></div>\';\n\n'
        '  h+=\'<div style="padding:16px;">'
    )
    new2 = (
        '  }\n'
        '  if(rows.length===0&&isOwnerOrAdmin()){\n'
        '    h+=\'<button onclick="talDuplicate(\'+d+\')" style="background:rgba(255,255,255,.15);border:1.5px solid rgba(255,255,255,.3);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:11px;color:#fff;">&#x1F4CB; Duplikat</button>\';\n'
        '  }\n\n'
        '  h+=\'</div></div>\';\n\n'
        '  h+=\'<div style="padding:16px;">'
    )
    if old2 in c:
        c = c.replace(old2, new2, 1)
        print(fpath.split('\\')[-1], '- PATCH 2 OK')
    else:
        errors.append('PATCH 2 not found')
        print(fpath.split('\\')[-1], '- PATCH 2 MISSING')

    if errors:
        print('ERRORS:', errors)
    else:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(fpath.split('\\')[-1], '- saved', len(c), 'chars')
    print()
