files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []

    # ─── PATCH 1: Add _visDivs filter inside _RD.forEach ───
    old1 = ("    if(!rows||rows.length===0) return;\n"
            "\n"
            "    // Ambil objective dari baris pertama (sama untuk semua KR dalam 1 divisi)")
    new1 = ("    if(!rows||rows.length===0) return;\n"
            "    if(_visDivs!==null&&_visDivs.indexOf(div)===-1) return; // filter by module access\n"
            "\n"
            "    // Ambil objective dari baris pertama (sama untuk semua KR dalam 1 divisi)")

    if old1 in c:
        c = c.replace(old1, new1, 1)
        print(fpath.split('\\')[-1], '- PATCH 1 OK (OKR _visDivs filter)')
    else:
        errors.append('PATCH 1 not found')
        print(fpath.split('\\')[-1], '- PATCH 1 MISSING')

    # ─── PATCH 2: Add MutationObserver in authApplyAccess ───
    old2 = ("  // OKR write buttons (Owner+Admin only)\n"
            "  ['okr-dup-btn','okr-tmpl-btn','okr-import-btn','okr-new-btn'].forEach(function(id){\n"
            "    var el=document.getElementById(id);\n"
            "    if(el) el.style.display=isOwnerOrAdmin()?'':'none';\n"
            "  });\n"
            "}")
    new2 = ("  // OKR write buttons (Owner+Admin only)\n"
            "  ['okr-dup-btn','okr-tmpl-btn','okr-import-btn','okr-new-btn'].forEach(function(id){\n"
            "    var el=document.getElementById(id);\n"
            "    if(el) el.style.display=isOwnerOrAdmin()?'':'none';\n"
            "  });\n"
            "  // MutationObserver: auto re-apply role restrictions when panel content re-renders\n"
            "  if(window._roleObserver){window._roleObserver.disconnect();window._roleObserver=null;}\n"
            "  if(!isOwnerOrAdmin()){\n"
            "    window._roleObserver=new MutationObserver(function(muts){\n"
            "      var panelIds={};\n"
            "      muts.forEach(function(m){\n"
            "        if(m.type!=='childList') return;\n"
            "        var el=m.target;\n"
            "        for(var i=0;i<10&&el&&el!==document.body;i++,el=el.parentElement){\n"
            "          if(el.id&&el.id.startsWith('panel-')&&el.id!=='panel-pengaturan'){\n"
            "            panelIds[el.id]=true;break;\n"
            "          }\n"
            "        }\n"
            "      });\n"
            "      Object.keys(panelIds).forEach(function(id){\n"
            "        applyPanelRoleUI(id.replace('panel-',''));\n"
            "      });\n"
            "    });\n"
            "    window._roleObserver.observe(document.body,{childList:true,subtree:true});\n"
            "  }\n"
            "}")

    if old2 in c:
        c = c.replace(old2, new2, 1)
        print(fpath.split('\\')[-1], '- PATCH 2 OK (MutationObserver)')
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
