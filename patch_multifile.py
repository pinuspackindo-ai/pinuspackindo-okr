import sys

files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

HELPERS = (
    "\n// ── MULTI-FILE UPLOAD HELPERS ──\n"
    "function _processImgFiles(files,cb){\n"
    "  var results=[],i=0;\n"
    "  function next(){\n"
    "    if(i>=files.length){cb(results);return;}\n"
    "    var f=files[i++];\n"
    "    var img=new Image(),url=URL.createObjectURL(f);\n"
    "    img.onload=function(){\n"
    "      var cv=document.createElement('canvas');\n"
    "      var mxW=1400,mxH=1050,w=img.width,h=img.height;\n"
    "      if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}\n"
    "      if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}\n"
    "      cv.width=w;cv.height=h;cv.getContext('2d').drawImage(img,0,0,w,h);\n"
    "      URL.revokeObjectURL(url);\n"
    "      results.push({name:f.name,data:cv.toDataURL('image/jpeg',0.78)});next();\n"
    "    };\n"
    "    img.onerror=function(){\n"
    "      URL.revokeObjectURL(url);\n"
    "      var r=new FileReader();\n"
    "      r.onload=function(e){results.push({name:f.name,data:e.target.result});next();};\n"
    "      r.readAsDataURL(f);\n"
    "    };\n"
    "    img.src=url;\n"
    "  }\n"
    "  next();\n"
    "}\n"
    "window._evStore={};\n"
    "function _evBtns(key,obj){\n"
    "  var evs=(obj&&obj.evidences&&obj.evidences.length>0)?obj.evidences\n"
    "    :((obj&&obj.evidence)?[{name:obj.evidenceName||'File',data:obj.evidence}]:[]);\n"
    "  window._evStore[key]=evs;\n"
    "  if(evs.length===0)return'<span style=\"color:var(--text-l);\">&#8212;</span>';\n"
    "  return'<span data-ek=\"'+key.replace(/\"/g,'')+'\">'+evs.map(function(ev,i){\n"
    "    return'<button onclick=\"_evView(this)\" data-ei=\"'+i+'\" style=\"background:none;border:1.5px solid var(--primary);color:var(--primary);border-radius:var(--radius-sm);padding:3px 8px;cursor:pointer;font-size:11px;font-family:var(--font);\">&#x1F441;'+(evs.length>1?' '+(i+1):'')+'</button>';\n"
    "  }).join('')+'</span>';\n"
    "}\n"
    "function _evView(btn){\n"
    "  var sp=btn.parentElement,key=sp&&sp.dataset.ek,idx=parseInt(btn.dataset.ei||'0');\n"
    "  var evs=window._evStore&&window._evStore[key];\n"
    "  if(!evs||!evs[idx])return;\n"
    "  var ev=evs[idx];\n"
    "  if(ev.data.startsWith('data:image/')){\n"
    "    var w=window.open('','_blank');\n"
    "    w.document.write('<html><body style=\"margin:0;background:#111;display:flex;justify-content:center;align-items:center;min-height:100vh;\"><img src=\"'+ev.data+'\" style=\"max-width:100%;max-height:100vh;object-fit:contain;\"></body></html>');\n"
    "  }else{\n"
    "    var a=document.createElement('a');a.href=ev.data;a.download=ev.name||'bukti';\n"
    "    document.body.appendChild(a);a.click();document.body.removeChild(a);\n"
    "  }\n"
    "}\n"
)

# Multi-file validation replacement (added at end: var file=_fs[0]; for backward compat)
VAL_NEW_WITH_RESET = (
    "var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;\n"
    "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}\n"
    "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');inp.value='';return;}\n"
    "  var file=_fs[0];"
)
VAL_NEW_NO_RESET = (
    "var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;\n"
    "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}\n"
    "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');return;}\n"
    "  var file=_fs[0];"
)

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    errors = []
    patches_ok = []

    # ─── 1. ADD HELPERS before okrInit() ───
    marker = '\nokrInit();\nauthInit();'
    if marker in c:
        c = c.replace(marker, HELPERS + marker, 1)
        patches_ok.append('1: helpers added')
    else:
        errors.append('1: okrInit marker not found')

    # ─── 2. VALIDATION REPLACEMENTS ───

    # Pattern A: "var file=inp.files[0]; if(!file) return;\n  if(file.size>5*...)...inp.value='';return;}"
    v_a = ("var file=inp.files[0]; if(!file) return;\n"
           "  if(file.size>5*1024*1024){notify('File terlalu besar (maks 5MB).','error');inp.value='';return;}")
    cnt = c.count(v_a); c = c.replace(v_a, VAL_NEW_WITH_RESET)
    patches_ok.append(f'2a: {cnt} validation (space+reset)')

    # Pattern B: "var file=inp.files[0];if(!file)return;\n  if(file.size>5*...)...inp.value='';return;}"
    v_b = ("var file=inp.files[0];if(!file)return;\n"
           "  if(file.size>5*1024*1024){notify('File terlalu besar (maks 5MB).','error');inp.value='';return;}")
    cnt = c.count(v_b); c = c.replace(v_b, VAL_NEW_WITH_RESET)
    patches_ok.append(f'2b: {cnt} validation (nospace+reset)')

    # Pattern C: "var file=inp.files[0];if(!file)return;\n  if(file.size>5*...)...return;}" (no inp.value)
    v_c = ("var file=inp.files[0];if(!file)return;\n"
           "  if(file.size>5*1024*1024){notify('File terlalu besar (maks 5MB).','error');return;}")
    cnt = c.count(v_c); c = c.replace(v_c, VAL_NEW_NO_RESET)
    patches_ok.append(f'2c: {cnt} validation (nospace+noreset)')

    # ─── 3. PATTERN A: Replace multi-line canvas blocks (store/distrib/warehouse) ───

    # storeUpload
    store_canvas_old = (
        "  var img_=new Image();\n"
        "  var url=URL.createObjectURL(file);\n"
        "  img_.onload=function(){\n"
        "    var canvas=document.createElement('canvas');\n"
        "    var mxW=1400,mxH=1050,w=img_.width,h=img_.height;\n"
        "    if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}\n"
        "    if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}\n"
        "    canvas.width=w;canvas.height=h;\n"
        "    canvas.getContext('2d').drawImage(img_,0,0,w,h);\n"
        "    URL.revokeObjectURL(url);\n"
        "    var b64=canvas.toDataURL('image/jpeg',0.78);\n"
        "    var d=_sg(storeCurSub,storeYear,month);\n"
        "    if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "    d.evidence=b64;d.evidenceName=file.name;\n"
        "    _ss(storeCurSub,storeYear,month,d);\n"
        "    storeRender();\n"
        "    notify('Bukti \"'+file.name+'\" berhasil diupload ✓');\n"
        "  };\n"
        "  img_.onerror=function(){\n"
        "    URL.revokeObjectURL(url);\n"
        "    var reader=new FileReader();\n"
        "    reader.onload=function(e){\n"
        "      var d=_sg(storeCurSub,storeYear,month);\n"
        "      if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "      d.evidence=e.target.result;d.evidenceName=file.name;\n"
        "      _ss(storeCurSub,storeYear,month,d);\n"
        "      storeRender();\n"
        "      notify('Bukti \"'+file.name+'\" berhasil diupload ✓');\n"
        "    };\n"
        "    reader.readAsDataURL(file);\n"
        "  };\n"
        "  img_.src=url;"
    )
    store_canvas_new = (
        "  _processImgFiles(_fs,function(results){\n"
        "    var d=_sg(storeCurSub,storeYear,month);\n"
        "    if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "    d.evidences=results;d.evidence=results[0]?results[0].data:'';d.evidenceName=results[0]?results[0].name:'';\n"
        "    _ss(storeCurSub,storeYear,month,d);\n"
        "    storeRender();\n"
        "    notify('Bukti berhasil diupload ✓');\n"
        "  });"
    )
    if store_canvas_old in c:
        c = c.replace(store_canvas_old, store_canvas_new, 1)
        patches_ok.append('3a: storeUpload canvas replaced')
    else:
        errors.append('3a: storeUpload canvas not found')

    # distribUpload
    distrib_canvas_old = (
        "  var img_=new Image();\n"
        "  var url=URL.createObjectURL(file);\n"
        "  img_.onload=function(){\n"
        "    var canvas=document.createElement('canvas');\n"
        "    var mxW=1400,mxH=1050,w=img_.width,h=img_.height;\n"
        "    if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}\n"
        "    if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}\n"
        "    canvas.width=w;canvas.height=h;\n"
        "    canvas.getContext('2d').drawImage(img_,0,0,w,h);\n"
        "    URL.revokeObjectURL(url);\n"
        "    var b64=canvas.toDataURL('image/jpeg',0.78);\n"
        "    var d=_dg(distribCurSub,distribYear,month);\n"
        "    if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "    d.evidence=b64;d.evidenceName=file.name;\n"
        "    _ds(distribCurSub,distribYear,month,d);\n"
        "    distribRender();\n"
        "    notify('Bukti \"'+file.name+'\" berhasil diupload ✓');\n"
        "  };\n"
        "  img_.onerror=function(){\n"
        "    URL.revokeObjectURL(url);\n"
        "    var reader=new FileReader();\n"
        "    reader.onload=function(e){\n"
        "      var d=_dg(distribCurSub,distribYear,month);\n"
        "      if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "      d.evidence=e.target.result;d.evidenceName=file.name;\n"
        "      _ds(distribCurSub,distribYear,month,d);\n"
        "      distribRender();\n"
        "      notify('Bukti \"'+file.name+'\" berhasil diupload ✓');\n"
        "    };\n"
        "    reader.readAsDataURL(file);\n"
        "  };\n"
        "  img_.src=url;"
    )
    distrib_canvas_new = (
        "  _processImgFiles(_fs,function(results){\n"
        "    var d=_dg(distribCurSub,distribYear,month);\n"
        "    if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "    d.evidences=results;d.evidence=results[0]?results[0].data:'';d.evidenceName=results[0]?results[0].name:'';\n"
        "    _ds(distribCurSub,distribYear,month,d);\n"
        "    distribRender();\n"
        "    notify('Bukti berhasil diupload ✓');\n"
        "  });"
    )
    if distrib_canvas_old in c:
        c = c.replace(distrib_canvas_old, distrib_canvas_new, 1)
        patches_ok.append('3b: distribUpload canvas replaced')
    else:
        errors.append('3b: distribUpload canvas not found')

    # warehouseUpload
    wh_canvas_old = (
        "  var img_=new Image();\n"
        "  var url=URL.createObjectURL(file);\n"
        "  img_.onload=function(){\n"
        "    var canvas=document.createElement('canvas');\n"
        "    var mxW=1400,mxH=1050,w=img_.width,h=img_.height;\n"
        "    if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}\n"
        "    if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}\n"
        "    canvas.width=w;canvas.height=h;\n"
        "    canvas.getContext('2d').drawImage(img_,0,0,w,h);\n"
        "    URL.revokeObjectURL(url);\n"
        "    var b64=canvas.toDataURL('image/jpeg',0.78);\n"
        "    var d=_wg(warehouseCurSub,warehouseYear,month);\n"
        "    if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "    d.evidence=b64;d.evidenceName=file.name;\n"
        "    _ws(warehouseCurSub,warehouseYear,month,d);\n"
        "    warehouseRender();\n"
        "    notify('Bukti \"'+file.name+'\" berhasil diupload ✓');\n"
        "  };\n"
        "  img_.onerror=function(){\n"
        "    URL.revokeObjectURL(url);\n"
        "    var reader=new FileReader();\n"
        "    reader.onload=function(e){\n"
        "      var d=_wg(warehouseCurSub,warehouseYear,month);\n"
        "      if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "      d.evidence=e.target.result;d.evidenceName=file.name;\n"
        "      _ws(warehouseCurSub,warehouseYear,month,d);\n"
        "      warehouseRender();\n"
        "      notify('Bukti \"'+file.name+'\" berhasil diupload ✓');\n"
        "    };\n"
        "    reader.readAsDataURL(file);\n"
        "  };\n"
        "  img_.src=url;"
    )
    wh_canvas_new = (
        "  _processImgFiles(_fs,function(results){\n"
        "    var d=_wg(warehouseCurSub,warehouseYear,month);\n"
        "    if(curVal!==undefined&&!isNaN(curVal)) d.value=curVal;\n"
        "    d.evidences=results;d.evidence=results[0]?results[0].data:'';d.evidenceName=results[0]?results[0].name:'';\n"
        "    _ws(warehouseCurSub,warehouseYear,month,d);\n"
        "    warehouseRender();\n"
        "    notify('Bukti berhasil diupload ✓');\n"
        "  });"
    )
    if wh_canvas_old in c:
        c = c.replace(wh_canvas_old, wh_canvas_new, 1)
        patches_ok.append('3c: warehouseUpload canvas replaced')
    else:
        errors.append('3c: warehouseUpload canvas not found')

    # ─── 4. INNER FUNCTION SIGNATURES ───
    cnt_sv = c.count('function _sv(b64){')
    c = c.replace('function _sv(b64){', 'function _sv(b64,_evs){')
    patches_ok.append(f'4a: {cnt_sv} _sv signatures updated')

    cnt_save = c.count('function _save(b64){')
    c = c.replace('function _save(b64){', 'function _save(b64,_evs){')
    patches_ok.append(f'4b: {cnt_save} _save signatures updated')

    # ─── 5. ADD EVIDENCES ARRAY BEFORE EVIDENCE STORAGE ───

    # Standard d.evidence=b64 (inside compact inner functions)
    cnt = c.count('d.evidence=b64;d.evidenceName=file.name;')
    c = c.replace(
        'd.evidence=b64;d.evidenceName=file.name;',
        'd.evidences=_evs||[];d.evidence=b64;d.evidenceName=file.name;'
    )
    patches_ok.append(f'5a: {cnt} d.evidence=b64 + evidences array')

    # row.evidence=b64 (gaWpUploadRow, hrdRecUploadRow, hrdKinUploadRow)
    cnt = c.count('row.evidence=b64;row.evidenceName=file.name;')
    c = c.replace(
        'row.evidence=b64;row.evidenceName=file.name;',
        'row.evidences=_evs||[];row.evidence=b64;row.evidenceName=file.name;'
    )
    patches_ok.append(f'5b: {cnt} row.evidence=b64 + evidences array')

    # rot.akurasiEv (invRot, finaccRot, gaRot)
    cnt = c.count('rot.akurasiEv=b64;rot.akurasiEvName=file.name;')
    c = c.replace(
        'rot.akurasiEv=b64;rot.akurasiEvName=file.name;',
        'rot.akurasiEvs=_evs||[];rot.akurasiEv=b64;rot.akurasiEvName=file.name;'
    )
    patches_ok.append(f'5c: {cnt} rot.akurasiEv + evidences array')

    # rot.ontimeEv
    cnt = c.count('rot.ontimeEv=b64;rot.ontimeEvName=file.name;')
    c = c.replace(
        'rot.ontimeEv=b64;rot.ontimeEvName=file.name;',
        'rot.ontimeEvs=_evs||[];rot.ontimeEv=b64;rot.ontimeEvName=file.name;'
    )
    patches_ok.append(f'5d: {cnt} rot.ontimeEv + evidences array')

    # ─── 6. COMPACT CANVAS BLOCK REPLACEMENTS ───

    # _sv with SEPARATE img_.src=url; line
    cv_sv_sep_old = (
        "  var img_=new Image();var url=URL.createObjectURL(file);\n"
        "  img_.onload=function(){var c=document.createElement('canvas');var mxW=1400,mxH=1050,w=img_.width,h=img_.height;"
        "if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}c.width=w;c.height=h;"
        "c.getContext('2d').drawImage(img_,0,0,w,h);URL.revokeObjectURL(url);_sv(c.toDataURL('image/jpeg',0.78));};\n"
        "  img_.onerror=function(){URL.revokeObjectURL(url);var r=new FileReader();r.onload=function(e){_sv(e.target.result);};r.readAsDataURL(file);};\n"
        "  img_.src=url;"
    )
    cv_sv_sep_new = "  _processImgFiles(_fs,function(results){_sv(results[0]?results[0].data:'',results);});"
    cnt = c.count(cv_sv_sep_old)
    c = c.replace(cv_sv_sep_old, cv_sv_sep_new)
    patches_ok.append(f'6a: {cnt} compact _sv (sep) canvas replaced')

    # _sv with img_.src=url; on SAME line as onerror
    cv_sv_same_old = (
        "  var img_=new Image();var url=URL.createObjectURL(file);\n"
        "  img_.onload=function(){var c=document.createElement('canvas');var mxW=1400,mxH=1050,w=img_.width,h=img_.height;"
        "if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}c.width=w;c.height=h;"
        "c.getContext('2d').drawImage(img_,0,0,w,h);URL.revokeObjectURL(url);_sv(c.toDataURL('image/jpeg',0.78));};\n"
        "  img_.onerror=function(){URL.revokeObjectURL(url);var r=new FileReader();r.onload=function(e){_sv(e.target.result);};r.readAsDataURL(file);};img_.src=url;"
    )
    cv_sv_same_new = "  _processImgFiles(_fs,function(results){_sv(results[0]?results[0].data:'',results);});"
    cnt = c.count(cv_sv_same_old)
    c = c.replace(cv_sv_same_old, cv_sv_same_new)
    patches_ok.append(f'6b: {cnt} compact _sv (same) canvas replaced')

    # _save with SEPARATE img_.src=url; line
    cv_save_sep_old = (
        "  var img_=new Image();var url=URL.createObjectURL(file);\n"
        "  img_.onload=function(){var c=document.createElement('canvas');var mxW=1400,mxH=1050,w=img_.width,h=img_.height;"
        "if(w>mxW){h=Math.round(h*mxW/w);w=mxW;}if(h>mxH){w=Math.round(w*mxH/h);h=mxH;}c.width=w;c.height=h;"
        "c.getContext('2d').drawImage(img_,0,0,w,h);URL.revokeObjectURL(url);_save(c.toDataURL('image/jpeg',0.78));};\n"
        "  img_.onerror=function(){URL.revokeObjectURL(url);var r=new FileReader();r.onload=function(e){_save(e.target.result);};r.readAsDataURL(file);};\n"
        "  img_.src=url;"
    )
    cv_save_sep_new = "  _processImgFiles(_fs,function(results){_save(results[0]?results[0].data:'',results);});"
    cnt = c.count(cv_save_sep_old)
    c = c.replace(cv_save_sep_old, cv_save_sep_new)
    patches_ok.append(f'6c: {cnt} compact _save (sep) canvas replaced')

    # ─── 7. finaccImplUpload (FileReader-only, no size check originally) ───
    fi_old = (
        "function finaccImplUpload(month,inp){\n"
        "  var file=inp.files[0];if(!file)return;\n"
        "  var y=finaccYear;\n"
        "  var reader=new FileReader();\n"
        "  reader.onload=function(e){\n"
        "    var valEl=document.getElementById('fa-impl-val-'+month);\n"
        "    var curVal=valEl&&valEl.value!==''?parseFloat(valEl.value):null;\n"
        "    var d=_fag('impl_reko_fa',y,month);\n"
        "    if(curVal!==null&&!isNaN(curVal))d.value=curVal;\n"
        "    d.evidence=e.target.result;d.evidenceName=file.name;\n"
        "    _fas('impl_reko_fa',y,month,d);okrSaveLS();finaccRenderImpl();\n"
        "    notify('\"'+file.name+'\" diupload ✓');\n"
        "  };\n"
        "  reader.readAsDataURL(file);\n"
        "}"
    )
    fi_new = (
        "function finaccImplUpload(month,inp){\n"
        "  var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;\n"
        "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}\n"
        "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');inp.value='';return;}\n"
        "  var y=finaccYear;\n"
        "  _processImgFiles(_fs,function(results){\n"
        "    var valEl=document.getElementById('fa-impl-val-'+month);\n"
        "    var curVal=valEl&&valEl.value!==''?parseFloat(valEl.value):null;\n"
        "    var d=_fag('impl_reko_fa',y,month);\n"
        "    if(curVal!==null&&!isNaN(curVal))d.value=curVal;\n"
        "    d.evidences=results;d.evidence=results[0]?results[0].data:'';d.evidenceName=results[0]?results[0].name:'';\n"
        "    _fas('impl_reko_fa',y,month,d);okrSaveLS();finaccRenderImpl();\n"
        "    notify('Bukti diupload ✓');\n"
        "  });\n"
        "}"
    )
    if fi_old in c:
        c = c.replace(fi_old, fi_new, 1)
        patches_ok.append('7: finaccImplUpload replaced')
    else:
        errors.append('7: finaccImplUpload not found')

    # ─── 8. IA FUNCTIONS (event.target.files) ───

    # iaRekoUpload
    ia_reko_old = (
        "function iaRekoUpload(event,i){\n"
        "  var file=event.target.files[0]; if(!file) return;\n"
        "  var reader=new FileReader();\n"
        "  reader.onload=function(e){\n"
        "    var data=iaRekoLoad(_iaCurYear,_iaCurMonth);\n"
        "    data.rows[i].evidence=e.target.result; data.rows[i].evidenceName=file.name;\n"
        "    iaRekoSave(_iaCurYear,_iaCurMonth,data); iaRekoRender();\n"
        "  }; reader.readAsDataURL(file);\n"
        "}"
    )
    ia_reko_new = (
        "function iaRekoUpload(event,i){\n"
        "  var _fs=Array.from(event.target.files||[]);if(_fs.length===0)return;\n"
        "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');event.target.value='';return;}\n"
        "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');event.target.value='';return;}\n"
        "  _processImgFiles(_fs,function(results){\n"
        "    var data=iaRekoLoad(_iaCurYear,_iaCurMonth);\n"
        "    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';\n"
        "    iaRekoSave(_iaCurYear,_iaCurMonth,data); iaRekoRender();\n"
        "  });\n"
        "}"
    )
    if ia_reko_old in c:
        c = c.replace(ia_reko_old, ia_reko_new, 1)
        patches_ok.append('8a: iaRekoUpload replaced')
    else:
        errors.append('8a: iaRekoUpload not found')

    # iaRotUpload
    ia_rot_old = (
        "function iaRotUpload(event,typeKey,i){\n"
        "  var file=event.target.files[0]; if(!file) return;\n"
        "  var reader=new FileReader();\n"
        "  reader.onload=function(e){\n"
        "    var data=iaRotLoad(typeKey,_iaCurYear,_iaCurMonth);\n"
        "    data.rows[i].evidence=e.target.result; data.rows[i].evidenceName=file.name;\n"
        "    iaRotSave(typeKey,_iaCurYear,_iaCurMonth,data); iaRotRender();\n"
        "  }; reader.readAsDataURL(file);\n"
        "}"
    )
    ia_rot_new = (
        "function iaRotUpload(event,typeKey,i){\n"
        "  var _fs=Array.from(event.target.files||[]);if(_fs.length===0)return;\n"
        "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');event.target.value='';return;}\n"
        "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');event.target.value='';return;}\n"
        "  _processImgFiles(_fs,function(results){\n"
        "    var data=iaRotLoad(typeKey,_iaCurYear,_iaCurMonth);\n"
        "    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';\n"
        "    iaRotSave(typeKey,_iaCurYear,_iaCurMonth,data); iaRotRender();\n"
        "  });\n"
        "}"
    )
    if ia_rot_old in c:
        c = c.replace(ia_rot_old, ia_rot_new, 1)
        patches_ok.append('8b: iaRotUpload replaced')
    else:
        errors.append('8b: iaRotUpload not found')

    # iaProjUpload
    ia_proj_old = (
        "function iaProjUpload(event,i){\n"
        "  var file=event.target.files[0]; if(!file) return;\n"
        "  var reader=new FileReader();\n"
        "  reader.onload=function(e){\n"
        "    var data=iaProjLoad(_iaCurYear,_iaCurMonth);\n"
        "    data.rows[i].evidence=e.target.result; data.rows[i].evidenceName=file.name;\n"
        "    okrData[iaProjKey(_iaCurYear,_iaCurMonth)]=data; okrSaveLS(); iaProjRender();\n"
        "  }; reader.readAsDataURL(file);\n"
        "}"
    )
    ia_proj_new = (
        "function iaProjUpload(event,i){\n"
        "  var _fs=Array.from(event.target.files||[]);if(_fs.length===0)return;\n"
        "  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');event.target.value='';return;}\n"
        "  if(_fs.some(function(f){return f.size>1024*1024;})){notify('Ukuran file maksimal 1 MB per file.','error');event.target.value='';return;}\n"
        "  _processImgFiles(_fs,function(results){\n"
        "    var data=iaProjLoad(_iaCurYear,_iaCurMonth);\n"
        "    data.rows[i].evidences=results;data.rows[i].evidence=results[0]?results[0].data:'';data.rows[i].evidenceName=results[0]?results[0].name:'';\n"
        "    okrData[iaProjKey(_iaCurYear,_iaCurMonth)]=data; okrSaveLS(); iaProjRender();\n"
        "  });\n"
        "}"
    )
    if ia_proj_old in c:
        c = c.replace(ia_proj_old, ia_proj_new, 1)
        patches_ok.append('8c: iaProjUpload replaced')
    else:
        errors.append('8c: iaProjUpload not found')

    # ─── 9. ADD multiple TO FILE INPUTS ───
    cnt_inp = c.count('type="file"')
    c = c.replace('type="file"', 'type="file" multiple')
    c = c.replace('type="file" multiple multiple', 'type="file" multiple')
    patches_ok.append(f'9: {cnt_inp} file inputs -> multiple')

    # ─── PRINT RESULTS ───
    name = fpath.split('\\')[-1]
    sys.stdout.buffer.write(('\n=== ' + name + ' ===\n').encode('utf-8'))
    for p in patches_ok:
        sys.stdout.buffer.write(('  OK: ' + p + '\n').encode('utf-8'))
    if errors:
        sys.stdout.buffer.write('  ERRORS:\n'.encode('utf-8'))
        for e in errors:
            sys.stdout.buffer.write(('  !! ' + e + '\n').encode('utf-8'))

    if not errors:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c)
        sys.stdout.buffer.write(('  Saved: ' + str(len(c)) + ' chars\n').encode('utf-8'))
    else:
        sys.stdout.buffer.write('  NOT SAVED due to errors\n'.encode('utf-8'))
