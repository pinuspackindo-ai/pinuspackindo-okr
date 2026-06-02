import re

files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

# ═══════════════════════════════════════════════════════════════
# COLLAPSED SIDEBAR CSS (added after .btn-logout:hover rule)
# ═══════════════════════════════════════════════════════════════
SB_CSS = (
    ".sb-toggle{background:none;border:none;color:rgba(255,255,255,.6);font-size:17px;"
    "cursor:pointer;padding:4px 7px;border-radius:4px;line-height:1;flex-shrink:0;margin-left:auto;}\n"
    ".sb-toggle:hover{color:#fff;background:rgba(255,255,255,.12);}\n"
    ".sidebar.collapsed{width:60px;overflow:hidden;}\n"
    ".sidebar.collapsed .sb-logo-content,.sidebar.collapsed .nav-label,"
    ".sidebar.collapsed .nav-text,.sidebar.collapsed .footer-text{display:none;}\n"
    ".sidebar.collapsed .sidebar-logo{padding:14px 0;justify-content:center;}\n"
    ".sidebar.collapsed .sidebar-nav{padding:8px 6px;}\n"
    ".sidebar.collapsed .nav-item{padding:10px;justify-content:center;gap:0;}\n"
    ".sidebar.collapsed .sidebar-footer{padding:10px 6px;text-align:center;}\n"
    ".sidebar.collapsed .btn-logout{font-size:0;padding:8px;width:auto;}\n"
    ".sidebar.collapsed .btn-logout .nav-icon{font-size:16px;}\n"
    ".sidebar.collapsed+.main{margin-left:60px;}\n"
)

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []
    patches_ok = []

    # ─── CSS 1: Add transition to .sidebar ───
    old_sb_css = ".sidebar{width:240px;background:var(--sb-bg);display:flex;flex-direction:column;\n  position:fixed;top:0;left:0;bottom:0;z-index:100;}"
    new_sb_css = ".sidebar{width:240px;background:var(--sb-bg);display:flex;flex-direction:column;\n  position:fixed;top:0;left:0;bottom:0;z-index:100;transition:width .2s ease;}"
    if old_sb_css in c:
        c = c.replace(old_sb_css, new_sb_css, 1)
        patches_ok.append('CSS1: sidebar transition added')
    else:
        errors.append('CSS1: .sidebar rule not found')

    # ─── CSS 2: Add transition to .main ───
    old_main_css = ".main{margin-left:240px;flex:1;display:flex;flex-direction:column;min-height:100vh;}"
    new_main_css = ".main{margin-left:240px;flex:1;display:flex;flex-direction:column;min-height:100vh;transition:margin-left .2s ease;}"
    if old_main_css in c:
        c = c.replace(old_main_css, new_main_css, 1)
        patches_ok.append('CSS2: .main transition added')
    else:
        errors.append('CSS2: .main rule not found')

    # ─── CSS 3: Inject collapsed sidebar styles ───
    old_logout_hover = ".btn-logout:hover{background:rgba(255,255,255,.10);color:#fff;}"
    new_logout_hover = old_logout_hover + "\n" + SB_CSS
    if old_logout_hover in c:
        c = c.replace(old_logout_hover, new_logout_hover, 1)
        patches_ok.append('CSS3: collapsed sidebar styles injected')
    else:
        errors.append('CSS3: .btn-logout:hover not found')

    # ─── HTML 1: Wrap sidebar-logo content + add toggle button ───
    old_logo = (
        '<aside class="sidebar" id="sidebar">\n'
        '  <div class="sidebar-logo">\n'
        '    <div class="logo-title">Pinus Packindo</div>\n'
        '    <div class="logo-sub">Tools OKR Pinus</div>\n'
        '    <div class="sb-user-badge" id="sb-user-badge" style="display:none;">\n'
        '      <div class="sb-user-avatar" id="sb-user-avatar">?</div>\n'
        '      <div style="min-width:0;">\n'
        '        <div class="sb-user-name" id="sb-user-name">—</div>\n'
        '        <div class="sb-user-role">User Aktif</div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>'
    )
    new_logo = (
        '<aside class="sidebar" id="sidebar">\n'
        '  <div class="sidebar-logo" style="display:flex;align-items:flex-start;gap:6px;">\n'
        '    <div class="sb-logo-content" style="flex:1;min-width:0;">\n'
        '      <div class="logo-title">Pinus Packindo</div>\n'
        '      <div class="logo-sub">Tools OKR Pinus</div>\n'
        '      <div class="sb-user-badge" id="sb-user-badge" style="display:none;">\n'
        '        <div class="sb-user-avatar" id="sb-user-avatar">?</div>\n'
        '        <div style="min-width:0;">\n'
        '          <div class="sb-user-name" id="sb-user-name">—</div>\n'
        '          <div class="sb-user-role">User Aktif</div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '    <button class="sb-toggle" id="sb-toggle" onclick="sidebarToggle()" title="Minimize menu">&#x2630;</button>\n'
        '  </div>'
    )
    if old_logo in c:
        c = c.replace(old_logo, new_logo, 1)
        patches_ok.append('HTML1: sidebar-logo restructured with toggle button')
    else:
        errors.append('HTML1: sidebar-logo block not found')

    # ─── HTML 2: Restructure nav-item buttons (add nav-icon + nav-text spans) ───
    # Pattern: >(one or more &#x...;) (text)</button>
    nav_pattern = re.compile(r'>((?:&#x[A-Fa-f0-9]+;(?:&#xFE0F;)?)+) ([^<]+)</button>')
    def nav_repl(m):
        icon = m.group(1)
        text = m.group(2)
        return '><span class="nav-icon">' + icon + '</span><span class="nav-text"> ' + text + '</span></button>'
    # Only apply inside the sidebar nav section
    nav_start = c.find('<nav class="sidebar-nav">')
    nav_end   = c.find('</nav>', nav_start) + len('</nav>')
    if nav_start != -1 and nav_end != -1:
        nav_block = c[nav_start:nav_end]
        new_nav_block, cnt = re.subn(nav_pattern, nav_repl, nav_block)
        c = c[:nav_start] + new_nav_block + c[nav_end:]
        patches_ok.append(f'HTML2: {cnt} nav-item buttons restructured')
    else:
        errors.append('HTML2: sidebar-nav block not found')

    # ─── HTML 3: Restructure sidebar-footer (logout button + footer text) ───
    old_footer = (
        '  <div class="sidebar-footer">\n'
        '    <button class="btn-logout" onclick="doLogout()">&#x1F6AA; Logout</button>\n'
        '    Upload: .xlsx / .xls / .csv<br>\n'
        '    Data diproses di browser<br>\n'
        '    Tidak dikirim ke server\n'
        '  </div>'
    )
    new_footer = (
        '  <div class="sidebar-footer">\n'
        '    <button class="btn-logout" onclick="doLogout()"><span class="nav-icon">&#x1F6AA;</span><span class="nav-text"> Logout</span></button>\n'
        '    <div class="footer-text" style="margin-top:4px;">Upload: .xlsx / .xls / .csv<br>Data diproses di browser<br>Tidak dikirim ke server</div>\n'
        '  </div>'
    )
    if old_footer in c:
        c = c.replace(old_footer, new_footer, 1)
        patches_ok.append('HTML3: sidebar-footer restructured')
    else:
        errors.append('HTML3: sidebar-footer not found')

    # ─── JS 1: Add sidebarToggle() before okrInit() ───
    js_toggle = (
        "\nfunction sidebarToggle(){\n"
        "  var sb=document.getElementById('sidebar');\n"
        "  sb.classList.toggle('collapsed');\n"
        "}\n"
    )
    marker = '\nokrInit();\nauthInit();'
    if marker in c:
        c = c.replace(marker, js_toggle + marker, 1)
        patches_ok.append('JS1: sidebarToggle() added')
    else:
        errors.append('JS1: okrInit() marker not found')

    # ─── JS 2: Update accessRender() — delete button for ALL users except Admin ───
    # Replace the isCustom-gated delete column with user!=='Admin' gate
    old_delete_col = (
        "    h+='<td style=\"padding:6px 8px;text-align:center;border-bottom:1px solid var(--border);'+bg+'\">';\n"
        "    if(isCustom){\n"
        "      h+='<button onclick=\"accessDeleteCustomUser(\\''+user.replace(/\\\\/g,'\\\\\\\\').replace(/'/g,'\\\\\\'')+'\\')"
        " style=\"background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:3px 7px;"
        "cursor:pointer;font-size:12px;font-family:var(--font);\">&#x1F5D1;</button>';\n"
        "    }else{\n"
        "      h+='<span style=\"color:var(--text-l);\">&#x2014;</span>';\n"
        "    }\n"
        "    h+='</td>';"
    )
    new_delete_col = (
        "    var _isDisabled=(okrData._disabledUsers||[]).indexOf(user)!==-1;\n"
        "    h+='<td style=\"padding:6px 8px;text-align:center;border-bottom:1px solid var(--border);'+bg+'\">';\n"
        "    if(user==='Admin'){\n"
        "      h+='<span style=\"color:var(--text-l);\">&#x2014;</span>';\n"
        "    }else if(_isDisabled){\n"
        "      h+='<button onclick=\"accessRestoreUser(\\''+user.replace(/\\\\/g,'\\\\\\\\').replace(/'/g,'\\\\\\'')+'\\')"
        " style=\"background:none;border:1.5px solid var(--success);color:var(--success);border-radius:var(--radius-sm);"
        "padding:3px 7px;cursor:pointer;font-size:11px;font-family:var(--font);\">Aktifkan</button>';\n"
        "    }else{\n"
        "      h+='<button onclick=\"accessDeleteUser(\\''+user.replace(/\\\\/g,'\\\\\\\\').replace(/'/g,'\\\\\\'')+'\\')"
        " style=\"background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:3px 7px;"
        "cursor:pointer;font-size:12px;font-family:var(--font);\">&#x1F5D1;</button>';\n"
        "    }\n"
        "    h+='</td>';"
    )
    if old_delete_col in c:
        c = c.replace(old_delete_col, new_delete_col, 1)
        patches_ok.append('JS2: delete column updated for all users')
    else:
        errors.append('JS2: delete column pattern not found')

    # ─── JS 3: Row style for disabled users ───
    old_row_open = (
        "    var isCustom=customUsers.indexOf(user)!==-1;\n"
        "    var bg=ri%2===0?'':'background:var(--bg);';\n"
        "    h+='<tr>';"
    )
    new_row_open = (
        "    var isCustom=customUsers.indexOf(user)!==-1;\n"
        "    var _dis=(okrData._disabledUsers||[]).indexOf(user)!==-1;\n"
        "    var bg=ri%2===0?'':'background:var(--bg);';\n"
        "    h+='<tr style=\"'+(_dis?'opacity:0.45;':'')+'\">'; "
    )
    if old_row_open in c:
        c = c.replace(old_row_open, new_row_open, 1)
        patches_ok.append('JS3: disabled user row styling added')
    else:
        errors.append('JS3: row open pattern not found')

    # ─── JS 4: Replace accessDeleteCustomUser + add accessDeleteUser + accessRestoreUser ───
    old_fns = (
        "function accessDeleteCustomUser(name){\n"
        "  if(!confirm('Hapus user \"'+name+'\"? Tindakan ini tidak dapat dibatalkan.')) return;\n"
        "  if(okrData._customUsers){\n"
        "    var idx=okrData._customUsers.indexOf(name);\n"
        "    if(idx!==-1) okrData._customUsers.splice(idx,1);\n"
        "  }\n"
        "  if(okrData._userAccess) delete okrData._userAccess[name];\n"
        "  if(okrData._userPwd) delete okrData._userPwd[name];\n"
        "  okrSaveLS();\n"
        "  accessRender();\n"
        "  notify('User \"'+name+'\" dihapus ✓');\n"
        "}"
    )
    new_fns = (
        "function accessDeleteUser(name){\n"
        "  if(!confirm('Hapus user \"'+name+'\"? User tidak dapat login. Admin dapat aktifkan kembali.')) return;\n"
        "  if(okrData._customUsers){\n"
        "    var ci=okrData._customUsers.indexOf(name);\n"
        "    if(ci!==-1) okrData._customUsers.splice(ci,1);\n"
        "  }\n"
        "  if(APP_USERS.indexOf(name)!==-1){\n"
        "    if(!okrData._disabledUsers) okrData._disabledUsers=[];\n"
        "    if(okrData._disabledUsers.indexOf(name)===-1) okrData._disabledUsers.push(name);\n"
        "  }\n"
        "  if(okrData._userPwd) delete okrData._userPwd[name];\n"
        "  okrSaveLS();accessRender();\n"
        "  notify('User \"'+name+'\" dihapus ✓');\n"
        "}\n"
        "function accessRestoreUser(name){\n"
        "  if(!okrData._disabledUsers) return;\n"
        "  var ri=okrData._disabledUsers.indexOf(name);\n"
        "  if(ri!==-1) okrData._disabledUsers.splice(ri,1);\n"
        "  okrSaveLS();accessRender();\n"
        "  notify('User \"'+name+'\" diaktifkan kembali ✓');\n"
        "}\n"
        "function accessDeleteCustomUser(name){accessDeleteUser(name);}"
    )
    if old_fns in c:
        c = c.replace(old_fns, new_fns, 1)
        patches_ok.append('JS4: accessDeleteUser + accessRestoreUser added')
    else:
        errors.append('JS4: accessDeleteCustomUser function not found')

    # ─── JS 5: Update authInit() to exclude disabled users from dropdown + session ───
    old_auth_users = (
        "    var allUsers=APP_USERS.concat(okrData._customUsers||[]);\n"
        "    allUsers.forEach(function(u){"
    )
    new_auth_users = (
        "    var _dis2=okrData._disabledUsers||[];\n"
        "    var allUsers=APP_USERS.filter(function(u){return _dis2.indexOf(u)===-1;}).concat(okrData._customUsers||[]);\n"
        "    allUsers.forEach(function(u){"
    )
    if old_auth_users in c:
        c = c.replace(old_auth_users, new_auth_users, 1)
        patches_ok.append('JS5: authInit disabled-user filter added')
    else:
        errors.append('JS5: authInit allUsers pattern not found')

    old_valid_users = "  var validUsers=APP_USERS.concat(okrData._customUsers||[]);"
    new_valid_users = (
        "  var _disV=okrData._disabledUsers||[];\n"
        "  var validUsers=APP_USERS.filter(function(u){return _disV.indexOf(u)===-1;}).concat(okrData._customUsers||[]);"
    )
    if old_valid_users in c:
        c = c.replace(old_valid_users, new_valid_users, 1)
        patches_ok.append('JS5b: session restore validUsers updated')
    else:
        errors.append('JS5b: validUsers pattern not found')

    # ─── JS 6: accessResetAll — also clear _disabledUsers ───
    old_reset = (
        "  if(!confirm('Reset semua akses ke default? Custom user tidak akan dihapus.')) return;\n"
        "  delete okrData._userAccess;\n"
        "  okrSaveLS();"
    )
    new_reset = (
        "  if(!confirm('Reset semua akses ke default? Custom user tidak akan dihapus, disabled user akan diaktifkan kembali.')) return;\n"
        "  delete okrData._userAccess;\n"
        "  delete okrData._disabledUsers;\n"
        "  okrSaveLS();"
    )
    if old_reset in c:
        c = c.replace(old_reset, new_reset, 1)
        patches_ok.append('JS6: accessResetAll clears _disabledUsers')
    else:
        errors.append('JS6: accessResetAll pattern not found')

    # ─── Print results ───
    name = fpath.split('\\')[-1]
    print(f'\n=== {name} ===')
    for p in patches_ok:
        print(f'  OK: {p}')
    if errors:
        print('  ERRORS:')
        for e in errors:
            print(f'  !! {e}')

    if not errors:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'  Saved: {len(c)} chars')
    else:
        print('  NOT saved due to errors')
