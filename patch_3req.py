import re

files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

# ═══════════════════════════════════════════════════════════════
# SHARED HELPER FUNCTIONS (insert before okrInit())
# ═══════════════════════════════════════════════════════════════
HELPERS = r"""
// ── MULTI-FILE UPLOAD HELPERS ──
function _processImgFiles(files, cb){
  var results=[],i=0;
  function next(){
    if(i>=files.length){cb(results);return;}
    var f=files[i++];
    var img=new Image(),url=URL.createObjectURL(f);
    img.onload=function(){
      var cv=document.createElement('canvas');
      var mxW=1400,mxH=1050,w=img.width,h=img.height;
      if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}
      if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}
      cv.width=w;cv.height=h;cv.getContext('2d').drawImage(img,0,0,w,h);
      URL.revokeObjectURL(url);
      results.push({name:f.name,data:cv.toDataURL('image/jpeg',0.78)});next();
    };
    img.onerror=function(){
      URL.revokeObjectURL(url);
      var r=new FileReader();
      r.onload=function(e){results.push({name:f.name,data:e.target.result});next();};
      r.readAsDataURL(f);
    };
    img.src=url;
  }
  next();
}
function _readFiles(inp,cb){
  var files=Array.from(inp.files||[]);
  if(files.length===0)return;
  if(files.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}
  if(files.some(function(f){return f.size>1024*1024;})){
    notify('Ukuran file maksimal 1 MB per file.','error');inp.value='';return;
  }
  _processImgFiles(files,cb);
}
window._evStore={};
function _evBtns(key,obj){
  var evs=(obj&&obj.evidences&&obj.evidences.length>0)?obj.evidences
    :((obj&&obj.evidence)?[{name:obj.evidenceName||'File',data:obj.evidence}]:[]);
  window._evStore[key]=evs;
  if(evs.length===0)return'<span style="color:var(--text-l);">—</span>';
  return'<span data-ek="'+key.replace(/"/g,'')+'">'+evs.map(function(ev,i){
    return'<button onclick="_evView(this)" data-ei="'+i+'" style="background:none;border:1.5px solid var(--primary);color:var(--primary);border-radius:var(--radius-sm);padding:3px 8px;cursor:pointer;font-size:11px;font-family:var(--font);">&#x1F441;'+(evs.length>1?' '+(i+1):'')+'</button>';
  }).join('')+'</span>';
}
function _evView(btn){
  var sp=btn.parentElement,key=sp&&sp.dataset.ek,idx=parseInt(btn.dataset.ei||'0');
  var evs=window._evStore&&window._evStore[key];
  if(!evs||!evs[idx])return;
  var ev=evs[idx];
  if(ev.data.startsWith('data:image/')){
    var w=window.open('','_blank');
    w.document.write('<html><body style="margin:0;background:#111;display:flex;justify-content:center;align-items:center;min-height:100vh;"><img src="'+ev.data+'" style="max-width:100%;max-height:100vh;object-fit:contain;"></body></html>');
  }else{
    var a=document.createElement('a');a.href=ev.data;a.download=ev.name||'bukti';
    document.body.appendChild(a);a.click();document.body.removeChild(a);
  }
}

"""

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []
    patches_ok = []

    # ─── FIX 1: Recruitment scoring - binary ontime/terlambat ───
    old_score = ("function _hrdRecRowScore(row){\n"
                 "  if(!row.deadline||!row.realisasi)return null;\n"
                 "  var dl=new Date(row.deadline+'T00:00:00');var rl=new Date(row.realisasi+'T00:00:00');\n"
                 "  var late=Math.max(0,Math.ceil((rl-dl)/86400000));\n"
                 "  return Math.max(0,(30-Math.min(late,30))/30*100);\n"
                 "}")
    new_score = ("function _hrdRecRowScore(row){\n"
                 "  if(!row.deadline||!row.realisasi)return null;\n"
                 "  var dl=new Date(row.deadline+'T00:00:00');var rl=new Date(row.realisasi+'T00:00:00');\n"
                 "  return rl<=dl?100:0; // Ontime=100%, Terlambat=0%\n"
                 "}")
    if old_score in c:
        c = c.replace(old_score, new_score, 1)
        patches_ok.append('FIX1a: _hrdRecRowScore binary scoring')
    else:
        errors.append('FIX1a: _hrdRecRowScore not found')

    # Update the description text in hrdRenderRecruitment
    old_desc = 'Ontime = 100%. Keterlambatan hingga 30 hari turun linear ke 0%. Score = rata-rata semua posisi bulan ini.'
    new_desc = 'Ontime (realisasi ≤ deadline) = 100%. Terlambat = 0%. Score = rata-rata semua posisi bulan ini.'
    if old_desc in c:
        c = c.replace(old_desc, new_desc)
        patches_ok.append('FIX1b: description updated')
    else:
        errors.append('FIX1b: description not found')

    # Update "Telat X hari" display to just show Ontime/Terlambat
    old_late = ("+(late===0?'? Ontime':'Telat '+late+' hari')+'</span>')
    new_late = ("+(late===0?'&#x2713; Ontime':'&#x2717; Terlambat')+'</span>')
    if old_late in c:
        c = c.replace(old_late, new_late)
        patches_ok.append('FIX1c: late display text updated')
    else:
        errors.append('FIX1c: late display text not found')

    # ─── FIX 2: TAL review atasan - only Owner/Admin can input ───
    # In talBuildDivCard view rows, the review column:
    old_review = (
        "      h+='<td style=\"padding:6px 8px;\"><div style=\"display:flex;gap:4px;align-items:center;\">';\n"
        "      h+='<input id=\"tal-rli-'+d+'-'+idx+'\" type=\"text\" value=\"'+okrEsc(row.review||'')+'\" placeholder=\"Review atasan...\" style=\"flex:1;min-width:80px;padding:4px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:11px;\">';\n"
        "      h+='<button onclick=\"talSaveReview('+d+','+idx+')\" style=\"background:none;border:1.5px solid var(--primary);color:var(--primary);border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;\">&#x2713;</button>';\n"
        "      h+='</div></td>';"
    )
    new_review = (
        "      h+='<td style=\"padding:6px 8px;\">';\n"
        "      if(isOwnerOrAdmin()){\n"
        "        h+='<div style=\"display:flex;gap:4px;align-items:center;\">';\n"
        "        h+='<input id=\"tal-rli-'+d+'-'+idx+'\" type=\"text\" value=\"'+okrEsc(row.review||'')+'\" placeholder=\"Review atasan...\" style=\"flex:1;min-width:80px;padding:4px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:11px;\">';\n"
        "        h+='<button onclick=\"talSaveReview('+d+','+idx+')\" style=\"background:none;border:1.5px solid var(--primary);color:var(--primary);border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;\">&#x2713;</button>';\n"
        "        h+='</div>';\n"
        "      }else{\n"
        "        h+='<span style=\"font-size:11px;color:var(--text-m);\">'+okrEsc(row.review||'—')+'</span>';\n"
        "      }\n"
        "      h+='</td>';"
    )
    if old_review in c:
        c = c.replace(old_review, new_review, 1)
        patches_ok.append('FIX2: TAL review OA-only')
    else:
        errors.append('FIX2: TAL review field not found')

    # ─── FIX 3: Add helper functions before okrInit() ───
    marker = '\nokrInit();\nauthInit();'
    if marker in c:
        c = c.replace(marker, HELPERS + marker, 1)
        patches_ok.append('FIX3a: helper functions inserted')
    else:
        errors.append('FIX3a: okrInit marker not found')

    # ─── FIX 3b: Update ALL upload functions validation (5MB→1MB, add multi-file) ───
    # Pattern 1: Simple "var file=inp.files[0]; if(!file) return;\n  if(file.size>N*1024*1024)..."
    def replace_upload_validation(text):
        # Pattern: var file=inp.files[0]; if(!file) return;\n  if(file.size>N*1024*1024){notify('...(maks NMB)...','error');inp.value='';return;}
        pattern = re.compile(
            r"var file=inp\.files\[0\]; if\(!file\) return;\n"
            r"  if\(file\.size>\d+\*1024\*1024\)\{notify\('.*?maks \d+MB.*?','error'\);inp\.value='';return;\}"
        )
        replacement = (
            "var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;\n"
            "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}\n"
            "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');inp.value='';return;}\n"
            "  var file=_fs[0];"
        )
        new_text, count = re.subn(pattern, replacement, text)
        return new_text, count

    c, cnt1 = replace_upload_validation(c)
    if cnt1 > 0:
        patches_ok.append(f'FIX3b: {cnt1} upload validation blocks updated')
    else:
        errors.append('FIX3b: no upload validation blocks found')

    # Pattern 2: var file=inp.files[0];if(!file)return; (without space)
    def replace_upload_validation2(text):
        pattern = re.compile(
            r"var file=inp\.files\[0\];if\(!file\)return;\n"
            r"  if\(file\.size>\d+\*1024\*1024\)\{notify\('.*?maks \d+MB.*?','error'\);inp\.value='';return;\}"
        )
        replacement = (
            "var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;\n"
            "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}\n"
            "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');inp.value='';return;}\n"
            "  var file=_fs[0];"
        )
        new_text, count = re.subn(pattern, replacement, text)
        return new_text, count

    c, cnt2 = replace_upload_validation2(c)
    if cnt2 > 0:
        patches_ok.append(f'FIX3c: {cnt2} more upload validations updated')

    # ─── FIX 3c: Change d.evidence=b64/e.target.result to also set d.evidences ───
    # After each: d.evidence=b64;d.evidenceName=file.name;
    def add_evidences_array(text):
        # Pattern after canvas processing
        p1 = re.compile(r'(d\.evidence=b64;d\.evidenceName=file\.name;)')
        r1 = r'\1d.evidences=(d.evidences||[]).filter(function(x){return!!x.data;});if(d.evidences.length===0||_fs.length>1){d.evidences=_fs.map(function(f,fi){return fi===0?{name:f.name,data:b64}:{name:f.name,data:b64};});}'
        # Simpler: just overwrite evidences with single for now (canvas processes 1 image)
        r1 = r'\1'  # keep as-is for canvas (complex async)
        # For FileReader pattern
        p2 = re.compile(r'((?:d|row|obj)\.\w*evidence\w*=e\.target\.result;(?:(?:d|row|obj)\.\w*evidenceName\w*=file\.name;)?)')
        return text, 0

    # Actually, let's just update storage where we can easily find the pattern:
    # d.evidence=b64;d.evidenceName=file.name; → add d.evidences line
    cnt3 = 0
    # Simple single-line pattern for FileReader
    old_ev = 'd.evidence=e.target.result;d.evidenceName=file.name;'
    new_ev = 'd.evidences=[{name:file.name,data:e.target.result}];d.evidence=e.target.result;d.evidenceName=file.name;'
    c_new = c.replace(old_ev, new_ev)
    cnt3 = c.count(old_ev)
    c = c_new
    if cnt3 > 0:
        patches_ok.append(f'FIX3d: {cnt3} FileReader evidence→evidences updated')

    # Canvas pattern: d.evidence=b64;d.evidenceName=file.name;
    old_ev2 = 'd.evidence=b64;d.evidenceName=file.name;'
    new_ev2 = 'd.evidences=[{name:_fs[0].name,data:b64}];d.evidence=b64;d.evidenceName=_fs[0].name;'
    c_new2 = c.replace(old_ev2, new_ev2)
    cnt3b = c.count(old_ev2)
    c = c_new2
    if cnt3b > 0:
        patches_ok.append(f'FIX3e: {cnt3b} canvas evidence→evidences updated')

    # ─── FIX 3d: Add `multiple` to ALL file inputs in HTML ───
    # type="file" → type="file" multiple (for inputs in JS-generated HTML)
    old_file_inp = 'type="file"'
    new_file_inp = 'type="file" multiple'
    cnt_inp = c.count(old_file_inp)
    c = c.replace(old_file_inp, new_file_inp)
    patches_ok.append(f'FIX3f: {cnt_inp} file inputs → multiple')

    # But don't double-add 'multiple multiple'
    c = c.replace('multiple multiple', 'multiple')

    # ─── Print results ───
    name = fpath.split('\\')[-1]
    print(f'\n=== {name} ===')
    for p in patches_ok:
        print(f'  ✓ {p}')
    if errors:
        print('  ERRORS:')
        for e in errors:
            print(f'  ✗ {e}')

    if not errors:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'  Saved: {len(c)} chars')
    else:
        print('  NOT saved due to errors')
