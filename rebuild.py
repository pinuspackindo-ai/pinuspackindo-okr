import subprocess, sys

# Get clean base from deb27dd
result = subprocess.run(
    ['git', 'show', 'deb27dd:index.html'],
    capture_output=True,
    cwd=r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1'
)
c = result.stdout.decode('utf-8')
print('Base size:', len(c))

errors = []

def replace_once(content, old, new, label):
    if old not in content:
        errors.append('NOT FOUND: ' + label)
        return content
    count = content.count(old)
    if count > 1:
        errors.append('MULTIPLE (' + str(count) + '): ' + label)
    return content.replace(old, new, 1)

# ─────────────────────────────────────────────────────
# PATCH 1: talRender() - add OA-only top buttons + dup section
# Insert BEFORE "// Render each division"
# ─────────────────────────────────────────────────────
old1 = "  // Render each division as a vertical card\n  divsToShow.forEach(function(d){"
new1 = """  // OA-only: single Tambah TAL + Duplikat top buttons
  if(isOwnerOrAdmin()){
    html+='<div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">';
    html+='<button onclick="talOpenAddForm()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2795; Tambah TAL</button>';
    html+='<button onclick="var s=document.getElementById(\\'tal-dup-section\\');s.style.display=s.style.display===\\'none\\'?\\'block\\':\\'none\\';" style="background:none;border:1.5px solid var(--border);color:var(--text);border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);">&#x1F4CB; Duplikat Bulan Lalu</button>';
    html+='</div>';
    html+='<div id="tal-dup-section" style="display:none;background:var(--bg2);border:1.5px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:16px;">';
    html+='<div style="font-size:13px;font-weight:700;color:var(--text);margin-bottom:10px;">&#x1F4CB; Duplikat dari Bulan Lalu</div>';
    html+='<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">';
    html+='<label style="font-size:12px;color:var(--text-m);">Divisi:</label>';
    html+='<select id="tal-dup-div" style="padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;">';
    divsToShow.forEach(function(idx){ html+='<option value="'+idx+'">'+okrEsc(TAL_DIV_NAMES[idx])+'</option>'; });
    html+='</select>';
    html+='<button onclick="talDupFromTop()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 14px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x1F4CB; Duplikat</button>';
    html+='</div></div>';
  }

  // Render each division as a vertical card
  divsToShow.forEach(function(d){"""

c = replace_once(c, old1, new1, 'talRender top buttons')

# ─────────────────────────────────────────────────────
# PATCH 2: talBuildDivCard - remove per-division Duplikat+Tambah TAL buttons
# Remove: if(rows.length===0){ h+='Duplikat button'; }  AND  h+='Tambah TAL button'
# ─────────────────────────────────────────────────────
old2 = """  if(rows.length===0){
    h+='<button onclick="talDuplicate('+d+')" style="background:rgba(255,255,255,.15);border:1.5px solid rgba(255,255,255,.3);border-radius:var(--radius-sm);padding:4px 10px;cursor:pointer;font-size:11px;color:#fff;">&#x1F4CB; Duplikat</button>';
  }
  h+='<button onclick="talFormForDiv('+d+')" style="background:rgba(255,255,255,.2);border:1.5px solid rgba(255,255,255,.4);border-radius:var(--radius-sm);padding:4px 12px;cursor:pointer;font-size:12px;color:#fff;font-weight:600;">&#x2795; Tambah TAL</button>';"""
new2 = ""  # Remove both buttons from division header

c = replace_once(c, old2, new2, 'remove per-div Duplikat+Tambah TAL buttons')

# ─────────────────────────────────────────────────────
# PATCH 3: talBuildDivCard - wrap edit/delete in OA conditional
# ─────────────────────────────────────────────────────
old3 = """        h+='<td style="padding:8px 10px;text-align:center;white-space:nowrap;">';
        h+='<button onclick="talEditRow('+d+','+idx+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 8px;cursor:pointer;font-size:11px;font-family:var(--font);">&#x270F;&#xFE0F;</button> ';
        h+='<button onclick="talDeleteRow('+d+','+idx+')" style="background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:4px 8px;cursor:pointer;font-size:11px;font-family:var(--font);">&#x1F5D1;</button>';
        h+='</td></"""
new3 = """        h+='<td style="padding:8px 10px;text-align:center;white-space:nowrap;">';
        if(isOwnerOrAdmin()){
          h+='<button onclick="talEditRow('+d+','+idx+')" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:4px 8px;cursor:pointer;font-size:11px;font-family:var(--font);">&#x270F;&#xFE0F;</button> ';
          h+='<button onclick="talDeleteRow('+d+','+idx+')" style="background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:4px 8px;cursor:pointer;font-size:11px;font-family:var(--font);">&#x1F5D1;</button>';
        }
        h+='</td></"""

c = replace_once(c, old3, new3, 'wrap talEditRow/talDeleteRow in OA conditional')

# ─────────────────────────────────────────────────────
# PATCH 4: Add talDupFromTop() function after talOpenAddForm
# ─────────────────────────────────────────────────────
old4 = "function talFormForDiv(d){"
new4 = """function talDupFromTop(){
  var sel=document.getElementById('tal-dup-div');
  if(!sel) return;
  var d=parseInt(sel.value);
  if(isNaN(d)) return;
  talDuplicate(d);
  var s=document.getElementById('tal-dup-section');
  if(s) s.style.display='none';
}
function talFormForDiv(d){"""

c = replace_once(c, old4, new4, 'add talDupFromTop function')

# ─────────────────────────────────────────────────────
# PATCH 5: Add applyPanelRoleUI() function before okrInit(); authInit();
# ─────────────────────────────────────────────────────
old5 = "okrInit();\nauthInit();"
new5 = """function applyPanelRoleUI(name){
  if(name==='dashboard'||name==='tal'||name==='pengaturan') return;
  if(isAdminUser()) return;
  var panel=document.getElementById('panel-'+name);
  if(!panel) return;
  panel.querySelectorAll('button').forEach(function(b){
    var oc=(b.getAttribute('onclick')||'').toLowerCase();
    var txt=b.textContent||b.innerText||'';
    var isEditDel=txt.indexOf('✏')!==-1||txt.indexOf('🗑')!==-1||
      /\\b(edit|hapus|delete|remove)[a-z]*(row|item|data|fn)?\\s*\\(/.test(oc);
    var isSave=/simpan|save|cancel|batal|submit|tutup|close/i.test(txt)||
      /simpan|save|cancel|batal/i.test(oc);
    if(isEditDel&&!isSave) b.style.display='none';
  });
}

okrInit();
authInit();"""

c = replace_once(c, old5, new5, 'add applyPanelRoleUI')

# ─────────────────────────────────────────────────────
# PATCH 6: showPanel - add applyPanelRoleUI call at end
# ─────────────────────────────────────────────────────
old6 = "  if(name==='pengaturan'){pengaturanInit();}\n}"
new6 = "  if(name==='pengaturan'){pengaturanInit();}\n  applyPanelRoleUI(name);\n}"

c = replace_once(c, old6, new6, 'add applyPanelRoleUI call in showPanel')

# ─────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────
print()
if errors:
    print('ERRORS:')
    for e in errors:
        print(' -', e)
    sys.exit(1)
else:
    print('All patches applied OK')

print('New size:', len(c))

# ─────────────────────────────────────────────────────
# Write templates/index.html (Flask version - keep doLogout as-is from base)
# Actually deb27dd has the Flask doLogout already
# ─────────────────────────────────────────────────────
with open(r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('templates/index.html written OK')

# ─────────────────────────────────────────────────────
# Write index.html (Vercel version - fix doLogout)
# ─────────────────────────────────────────────────────
c_root = c.replace(
    "function doLogout(){\n  sessionStorage.removeItem('okrLoginUser');\n  try{await fetch('/logout',{method:'POST'});}catch(e){}\n  location.reload();\n}",
    "function doLogout(){\n  sessionStorage.removeItem('okrLoginUser');\n  location.reload();\n}"
)
if len(c_root) == len(c):
    # Try alternate
    c_root = c.replace(
        "try{await fetch('/logout',{method:'POST'});}catch(e){}\n  location.reload();",
        "location.reload();"
    )

with open(r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html', 'w', encoding='utf-8') as f:
    f.write(c_root)
print('index.html written OK, size:', len(c_root))

# ─────────────────────────────────────────────────────
# Verify
# ─────────────────────────────────────────────────────
checks = ['isOwnerOrAdmin','ACCESS_MODULES','authGetVisibleOKRDivs',
          'talDupFromTop','accessRender','applyPanelRoleUI','iaInit',
          'tal-dup-section','APP_USERS','applyPanelRoleUI(name)']
print()
print('Verification:')
for k in checks:
    idx = c_root.find(k)
    print(' ', k, ':', 'OK' if idx>=0 else 'MISSING')

import re
doctypes = len(re.findall('<!DOCTYPE', c_root, re.IGNORECASE))
print('  DOCTYPE count:', doctypes, '(should be 1)')
corrupt = c_root.find('if(isOwnerOrAdmin()){} lang=')
print('  Corruption marker:', 'FOUND (BAD!)' if corrupt>=0 else 'NOT FOUND (clean)')
