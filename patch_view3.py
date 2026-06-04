# -*- coding: utf-8 -*-
files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

REPL = []

# ---- #3 Dashboard selalu bulan berjalan ----
REPL.append((
    "  if(name==='dashboard'){okrLoad();okrRender();}",
    "  if(name==='dashboard'){okrCurYear=new Date().getFullYear();okrCurMonth=new Date().getMonth()+1;var _ty=document.getElementById('okr-f-tahun');if(_ty)_ty.value=okrCurYear;var _tb=document.getElementById('okr-f-bulan');if(_tb)_tb.value=okrCurMonth;okrLoad();okrRender();}",
    'P3 dashboard reset bulan'))

# ---- #1 purchDownloadFile -> view online ----
REPL.append((
    """  if(!b64){notify('File tidak tersedia','error');return;}
  var data=b64.indexOf(',')!==-1?b64.split(',')[1]:b64;
  var binary=atob(data);var ab=new ArrayBuffer(binary.length);var view=new Uint8Array(ab);
  for(var i=0;i<binary.length;i++)view[i]=binary.charCodeAt(i);
  var blob=new Blob([ab]);var url=URL.createObjectURL(blob);
  var a=document.createElement('a');a.href=url;a.download=fname;a.click();
  setTimeout(function(){URL.revokeObjectURL(url);},1000);""",
    "  _viewFileOnline(b64,fname);",
    'P1 purchDownloadFile view online'))

# ---- #2a HRD kdk: simpan evs array per section ----
REPL.append((
    """    if(section==='abs'){d.abs.ev=b64;d.abs.evName=file.name;}
    else if(section==='kep'){d.kep.ev=b64;d.kep.evName=file.name;}
    else{d.snk.ev=b64;d.snk.evName=file.name;}""",
    """    if(section==='abs'){d.abs.ev=b64;d.abs.evName=file.name;d.abs.evs=_apEv(d.abs.evs,_evs);}
    else if(section==='kep'){d.kep.ev=b64;d.kep.evName=file.name;d.kep.evs=_apEv(d.kep.evs,_evs);}
    else{d.snk.ev=b64;d.snk.evName=file.name;d.snk.evs=_apEv(d.snk.evs,_evs);}""",
    'P2a hrdKdk store evs'))

# ---- #2a HRD kdk view: dari array ----
REPL.append((
    """function hrdKdkViewEv(mi,section){
  var d=_hrdKdkG(hrdYear,mi);
  var ev=section==='abs'?d.abs.ev:section==='kep'?d.kep.ev:d.snk.ev;
  var evName=section==='abs'?d.abs.evName:section==='kep'?d.kep.evName:d.snk.evName;
  if(!ev){notify('Tidak ada bukti.','error');return;}
  _viewEvs(ev?[{name:evName||'Bukti',data:ev}]:[]);
}""",
    """function hrdKdkViewEv(mi,section){
  var d=_hrdKdkG(hrdYear,mi);
  var sec=section==='abs'?d.abs:section==='kep'?d.kep:d.snk;
  var evs=(sec.evs&&sec.evs.length>0)?sec.evs:(sec.ev?[{name:sec.evName||'Bukti',data:sec.ev}]:[]);
  if(evs.length===0){notify('Tidak ada bukti.','error');return;}
  _viewEvs(evs);
}""",
    'P2a hrdKdk view array'))

# ---- #2b Purchasing impl reko: upload multi-file ----
REPL.append((
    """function purchImplEvidenceChange(month,inp){
  var file=inp.files[0];if(!file)return;
  var y=purchasingYear;
  var reader=new FileReader();
  reader.onload=function(e){
    var valEl=document.getElementById('pir-val-'+month);
    var curVal=valEl&&valEl.value!==''?parseFloat(valEl.value):null;
    var d=_pgIr(y,month);
    if(curVal!==null&&!isNaN(curVal))d.value=curVal;
    d.evidence=e.target.result;d.evidenceName=file.name;
    _psIr(y,month,d);okrSaveLS();purchImplRender();
    notify('"'+file.name+'" diupload ✓');
  };
  reader.readAsDataURL(file);
}""",
    """function purchImplEvidenceChange(month,inp){
  var _fs=Array.from(inp.files||[]);if(_fs.length===0)return;
  if(_fs.length>3){notify('Maksimal 3 file per upload.','error');inp.value='';return;}
  if(_fs.some(function(f){return f.size>500*1024;})){notify('Ukuran file maksimal 500 KB per file.','error');inp.value='';return;}
  var y=purchasingYear;
  _processImgFiles(_fs,function(results){
    var valEl=document.getElementById('pir-val-'+month);
    var curVal=valEl&&valEl.value!==''?parseFloat(valEl.value):null;
    var d=_pgIr(y,month);
    if(curVal!==null&&!isNaN(curVal))d.value=curVal;
    d.evidences=_apEv(d.evidences,results);
    d.evidence=d.evidences[0]?d.evidences[0].data:'';d.evidenceName=d.evidences[0]?d.evidences[0].name:'';
    _psIr(y,month,d);okrSaveLS();purchImplRender();
    notify(results.length+' bukti diupload ✓');
  });
}
function purchImplViewEv(m){var d=_pgIr(purchasingYear,m);var evs=(d.evidences&&d.evidences.length>0)?d.evidences:(d.evidence?[{name:d.evidenceName||'Bukti',data:d.evidence}]:[]);_viewEvs(evs);}""",
    'P2b implReko upload multi + view fn'))

# ---- #2b impl reko view button -> purchImplViewEv ----
REPL.append((
    "<button onclick=\"purchDownloadFile(\\'pir\\',\\'ev\\','+m+')\" style=\"font-size:10px;background:var(--primary-l);border:1px solid var(--primary);color:var(--primary);border-radius:4px;padding:2px 6px;cursor:pointer;\">View</button>",
    "<button onclick=\"purchImplViewEv('+m+')\" style=\"font-size:10px;background:var(--primary-l);border:1px solid var(--primary);color:var(--primary);border-radius:4px;padding:2px 6px;cursor:pointer;\">View</button>",
    'P2b implReko view button'))

# ---- build stamp ----
REPL.append(('Build: 2026-06-05-v7','Build: 2026-06-05-v8',False if False else True))

for fpath in files:
    with open(fpath,'r',encoding='utf-8') as f: c=f.read()
    ok=[];bad=[]
    for item in REPL:
        old=item[0]; new=item[1]; label=item[2]
        if old in c:
            c=c.replace(old,new)
            ok.append(label)
        else:
            bad.append(label)
    name='templates/index.html' if 'templates' in fpath else 'index.html'
    print('=== '+name+' ===')
    for p in ok: print('  OK',p)
    for b in bad: print('  MISSING:',b)
    if not bad:
        with open(fpath,'w',encoding='utf-8') as f: f.write(c)
        print('  Saved',len(c))
    else: print('  NOT saved')
