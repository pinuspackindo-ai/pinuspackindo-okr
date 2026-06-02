files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []

    # ─── PATCH 1: Add MODULE_OKR_DIV + MODULE_TAL_DIV maps after USER_TAL_DIVS ───
    old1 = ("var USER_OKR_DIVISION={\n"
            "  'Owner':null,'HRD':'HRD','Internal Audit':null,\n"
            "  'General Affair':'General Affair','Purchasing':'Purchasing',\n"
            "  'Inventory':'Inventory','Finance & Accounting':'Finance & Accounting',\n"
            "  'Store':'Store','Warehouse':'Warehouse','Sales':'Distribution Sales','Admin':null\n"
            "};\n"
            "// TAL division indices user \"owns\" (null=all)\n"
            "var USER_TAL_DIVS={\n"
            "  'Owner':null,'HRD':[3],'Internal Audit':null,\n"
            "  'General Affair':[4],'Purchasing':[5],\n"
            "  'Inventory':[],'Finance & Accounting':[2],\n"
            "  'Store':[0],'Warehouse':[7],'Sales':[1],'Admin':null\n"
            "};")

    new1 = ("var USER_OKR_DIVISION={\n"
            "  'Owner':null,'HRD':'HRD','Internal Audit':null,\n"
            "  'General Affair':'General Affair','Purchasing':'Purchasing',\n"
            "  'Inventory':'Inventory','Finance & Accounting':'Finance & Accounting',\n"
            "  'Store':'Store','Warehouse':'Warehouse','Sales':'Distribution Sales','Admin':null\n"
            "};\n"
            "// TAL division indices user \"owns\" (null=all)\n"
            "var USER_TAL_DIVS={\n"
            "  'Owner':null,'HRD':[3],'Internal Audit':null,\n"
            "  'General Affair':[4],'Purchasing':[5],\n"
            "  'Inventory':[],'Finance & Accounting':[2],\n"
            "  'Store':[0],'Warehouse':[7],'Sales':[1],'Admin':null\n"
            "};\n"
            "// Module key -> OKR division name\n"
            "var MODULE_OKR_DIV={\n"
            "  'store':'Store','distrib':'Distribution Sales','warehouse':'Warehouse',\n"
            "  'inventory':'Inventory','purchasing':'Purchasing',\n"
            "  'financeacc':'Finance & Accounting','generalaffair':'General Affair',\n"
            "  'hrd':'HRD','ia':'Internal Audit'\n"
            "};\n"
            "// Module key -> TAL division index\n"
            "var MODULE_TAL_DIV={\n"
            "  'store':0,'distrib':1,'financeacc':2,'hrd':3,\n"
            "  'generalaffair':4,'purchasing':5,'warehouse':7\n"
            "};")

    if old1 in c:
        c = c.replace(old1, new1, 1)
        print(fpath.split('\\')[-1], '- PATCH 1 OK (add MODULE maps)')
    else:
        errors.append('PATCH 1 not found')

    # ─── PATCH 2: Replace authGetVisibleOKRDivs + authGetVisibleTALDivs ───
    old2 = ("function authGetVisibleOKRDivs(){\n"
            "  if(!APP_CUR_USER) return [];\n"
            "  if(authCanSeeAllOKR()) return null; // null = all\n"
            "  var own=USER_OKR_DIVISION[APP_CUR_USER];\n"
            "  return own?[own]:[];\n"
            "}\n"
            "function authGetVisibleTALDivs(){\n"
            "  if(!APP_CUR_USER) return null;\n"
            "  if(authCanSeeAllOKR()) return null; // null = all\n"
            "  var divs=USER_TAL_DIVS[APP_CUR_USER];\n"
            "  return (divs===null||divs===undefined)?null:divs;\n"
            "}\n")

    new2 = ("function authGetVisibleOKRDivs(){\n"
            "  if(!APP_CUR_USER) return [];\n"
            "  var acc=authGetAccess(APP_CUR_USER);\n"
            "  if(acc.okrAll) return null; // see all divisions\n"
            "  var mods=acc.modules||[];\n"
            "  var divs=[];\n"
            "  mods.forEach(function(m){\n"
            "    if(MODULE_OKR_DIV[m]&&divs.indexOf(MODULE_OKR_DIV[m])===-1)\n"
            "      divs.push(MODULE_OKR_DIV[m]);\n"
            "  });\n"
            "  return divs;\n"
            "}\n"
            "function authGetVisibleTALDivs(){\n"
            "  if(!APP_CUR_USER) return null;\n"
            "  var acc=authGetAccess(APP_CUR_USER);\n"
            "  if(acc.okrAll) return null; // see all TAL divisions\n"
            "  var mods=acc.modules||[];\n"
            "  var divs=[];\n"
            "  mods.forEach(function(m){\n"
            "    if(MODULE_TAL_DIV[m]!==undefined&&divs.indexOf(MODULE_TAL_DIV[m])===-1)\n"
            "      divs.push(MODULE_TAL_DIV[m]);\n"
            "  });\n"
            "  return divs;\n"
            "}\n")

    if old2 in c:
        c = c.replace(old2, new2, 1)
        print(fpath.split('\\')[-1], '- PATCH 2 OK (rewrite authGetVisible)')
    else:
        errors.append('PATCH 2 not found')

    # ─── PATCH 3: Fix applyPanelRoleUI - isOwnerOrAdmin + cover all panels ───
    old3 = ("function applyPanelRoleUI(name){\n"
            "  if(name==='dashboard'||name==='tal'||name==='pengaturan') return;\n"
            "  if(isAdminUser()) return;\n"
            "  var panel=document.getElementById('panel-'+name);\n"
            "  if(!panel) return;\n"
            "  panel.querySelectorAll('button').forEach(function(b){\n"
            "    var oc=(b.getAttribute('onclick')||'').toLowerCase();\n"
            "    var txt=b.textContent||b.innerText||'';\n"
            "    var isEditDel=txt.indexOf('✏')!==-1||txt.indexOf('\U0001f5d1')!==-1||\n"
            "      /\\b(edit|hapus|delete|remove)[a-z]*(row|item|data|fn)?\\s*\\(/.test(oc);\n"
            "    var isSave=/simpan|save|cancel|batal|submit|tutup|close/i.test(txt)||\n"
            "      /simpan|save|cancel|batal/i.test(oc);\n"
            "    if(isEditDel&&!isSave) b.style.display='none';\n"
            "  });\n"
            "}")

    new3 = ("function applyPanelRoleUI(name){\n"
            "  if(name==='pengaturan') return;\n"
            "  if(isOwnerOrAdmin()) return;\n"
            "  var panel=document.getElementById('panel-'+name);\n"
            "  if(!panel) return;\n"
            "  panel.querySelectorAll('button').forEach(function(b){\n"
            "    var oc=(b.getAttribute('onclick')||'').toLowerCase();\n"
            "    var txt=b.textContent||b.innerText||'';\n"
            "    var isEditDel=txt.indexOf('✏')!==-1||txt.indexOf('\U0001f5d1')!==-1||\n"
            "      /\\b(edit|hapus|delete|remove)[a-z]*(row|item|data|fn)?\\s*\\(/.test(oc);\n"
            "    var isSave=/simpan|save|cancel|batal|submit|tutup|close/i.test(txt)||\n"
            "      /simpan|save|cancel|batal/i.test(oc);\n"
            "    if(isEditDel&&!isSave) b.style.display='none';\n"
            "  });\n"
            "}")

    if old3 in c:
        c = c.replace(old3, new3, 1)
        print(fpath.split('\\')[-1], '- PATCH 3 OK (fix applyPanelRoleUI)')
    else:
        errors.append('PATCH 3 not found - trying alternate')
        # Try finding it another way
        idx = c.find('function applyPanelRoleUI')
        if idx >= 0:
            end = c.find('\n}', idx) + 2
            snippet = c[idx:end]
            print('  Found at', idx, ':', repr(snippet[:100]))
        else:
            print('  NOT FOUND at all')

    if errors:
        print('ERRORS:', errors)
    else:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(fpath.split('\\')[-1], '- saved', len(c), 'chars')
    print()
