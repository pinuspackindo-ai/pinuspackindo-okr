files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

# ── P1: anyEditing harus cek isOwnerOrAdmin() ────────────────
OLD_ANY_EDITING = "  var anyEditing=rows.some(function(r){return r.editing;});"
NEW_ANY_EDITING = "  var anyEditing=isOwnerOrAdmin()&&rows.some(function(r){return r.editing;});"

# ── P2: edit row hanya untuk OA ──────────────────────────────
OLD_ROW_IF = "  rows.forEach(function(row,idx){\n    if(row.editing){"
NEW_ROW_IF = "  rows.forEach(function(row,idx){\n    if(row.editing&&isOwnerOrAdmin()){"

# ── P3: progress cell — gate dengan authCanFillTALProgress ───
OLD_PRG_CELL = (
    "      h+='<td style=\"padding:6px 8px;text-align:center;\"><div style=\"display:inline-flex;align-items:center;gap:4px;\">';\n"
    "      h+='<input id=\"tal-pli-'+d+'-'+idx+'\" type=\"number\" min=\"0\" max=\"100\" step=\"0.01\" value=\"'+(hasPrg?row.progress:'')+'"
    "\" placeholder=\"%\" style=\"width:62px;padding:4px 6px;border:1.5px solid '+(hasPrg?'var(--primary)':'var(--border)')+';border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;text-align:center;\">';\n"
    "      h+='<button onclick=\"talSaveProgress('+d+','+idx+')\" style=\"background:var(--primary);border:none;color:#fff;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:12px;line-height:1;display:flex;align-items:center;justify-content:center;flex-shrink:0;\">&#x2713;</button>';\n"
    "      h+='</div></td>';"
)
NEW_PRG_CELL = (
    "      h+='<td style=\"padding:6px 8px;text-align:center;\">';\n"
    "      if(authCanFillTALProgress(d)){\n"
    "        h+='<div style=\"display:inline-flex;align-items:center;gap:4px;\">';\n"
    "        h+='<input id=\"tal-pli-'+d+'-'+idx+'\" type=\"number\" min=\"0\" max=\"100\" step=\"0.01\" value=\"'+(hasPrg?row.progress:'')+'"
    "\" placeholder=\"%\" style=\"width:62px;padding:4px 6px;border:1.5px solid '+(hasPrg?'var(--primary)':'var(--border)')+';border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;text-align:center;\">';\n"
    "        h+='<button onclick=\"talSaveProgress('+d+','+idx+')\" style=\"background:var(--primary);border:none;color:#fff;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:12px;line-height:1;display:flex;align-items:center;justify-content:center;flex-shrink:0;\">&#x2713;</button>';\n"
    "        h+='</div>';\n"
    "      }else{\n"
    "        h+='<span style=\"color:var(--text-m);font-size:12px;\">'+(hasPrg?row.progress+'%':'—')+'</span>';\n"
    "      }\n"
    "      h+='</td>';"
)

# ── P4: tambah authCanFillTALProgress sebelum talBuildDivCard ─
# USER_TAL_DIVS mapping yang ada:
# 'HRD':[3], 'General Affair':[4], 'Purchasing':[5],
# 'Finance & Accounting':[2], 'Store':[0], 'Warehouse':[7], 'Sales':[1]
# 'Inventory':[], 'Internal Audit':null (sees all, fill only idx 12)
FN_CAN_FILL = (
    "\nfunction authCanFillTALProgress(d){\n"
    "  if(!APP_CUR_USER) return false;\n"
    "  if(isOwnerOrAdmin()) return true;\n"
    "  // Users with explicit array in USER_TAL_DIVS -> fill progress for those divisions\n"
    "  var divs=USER_TAL_DIVS[APP_CUR_USER];\n"
    "  if(divs===null){\n"
    "    // null means 'see all' but fill only own division\n"
    "    var _own={'Internal Audit':[12]};\n"
    "    var own=_own[APP_CUR_USER];\n"
    "    if(own===undefined) return true; // truly unrestricted (e.g. future role)\n"
    "    return own.indexOf(d)!==-1;\n"
    "  }\n"
    "  if(!divs||divs.length===0) return false;\n"
    "  return divs.indexOf(d)!==-1;\n"
    "}\n"
)

OLD_BUILD_FN = "\nfunction talBuildDivCard(d,y,m){"
NEW_BUILD_FN = FN_CAN_FILL + "\nfunction talBuildDivCard(d,y,m){"

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []
    patches_ok = []

    def do(old, new, label):
        if old in c:
            return c.replace(old, new, 1), label + ' OK'
        return c, '!! ' + label + ' NOT FOUND'

    c, m = do(OLD_ANY_EDITING, NEW_ANY_EDITING, 'P1: anyEditing gated by isOwnerOrAdmin'); (patches_ok if m.startswith('P') else errors).append(m)
    c, m = do(OLD_ROW_IF,      NEW_ROW_IF,      'P2: edit row gated by isOwnerOrAdmin');  (patches_ok if m.startswith('P') else errors).append(m)
    c, m = do(OLD_PRG_CELL,    NEW_PRG_CELL,    'P3: progress cell gated by authCanFillTALProgress'); (patches_ok if m.startswith('P') else errors).append(m)
    c, m = do(OLD_BUILD_FN,    NEW_BUILD_FN,    'P4: authCanFillTALProgress function added'); (patches_ok if m.startswith('P') else errors).append(m)

    name = 'templates/index.html' if 'templates' in fpath else 'index.html'
    print(f'\n=== {name} ===')
    for p in patches_ok: print(f'  OK: {p}')
    if errors:
        print('  ERRORS:')
        for e in errors: print(f'  {e}')

    if not errors:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'  Saved: {len(c)} chars')
    else:
        print('  NOT saved')
