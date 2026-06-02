files = [
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\index.html',
    r'C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1\templates\index.html',
]

NEW_SECTION = r"""function talRender(){
  var wrap=document.getElementById('tal-content');if(!wrap)return;
  var divsToShow=talGetVisibleDivs();

  // Check if module is empty for current month
  var moduleEmpty=divsToShow.every(function(d){
    return (_talG(d,talYear,talMonth).rows||[]).length===0;
  });

  // Build add form division options
  var divOpts='';
  divsToShow.forEach(function(i){
    divOpts+='<option value="'+i+'">'+okrEsc(TAL_DIV_NAMES[i])+'</option>';
  });

  var html='';

  // Hidden add form (top)
  html+='<div id="tal-add-form" style="display:none;background:var(--bg2);border:1.5px solid var(--primary);border-radius:var(--radius);padding:20px;margin-bottom:20px;">';
  html+='<div style="font-size:14px;font-weight:700;color:var(--text);margin-bottom:14px;">&#x1F4CB; Tambah TAL Baru</div>';
  html+='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:12px;">';
  html+='<div><label style="font-size:11px;color:var(--text-m);font-weight:600;">Nama Divisi</label><select id="tal-form-div" style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;">'+divOpts+'</select></div>';
  html+='<div style="grid-column:span 2;"><label style="font-size:11px;color:var(--text-m);font-weight:600;">Deskripsi TAL</label><input type="text" id="tal-form-tal" placeholder="Deskripsi TAL..." style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;"></div>';
  html+='<div><label style="font-size:11px;color:var(--text-m);font-weight:600;">Deadline</label><input type="date" id="tal-form-dl" style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;"></div>';
  html+='<div><label style="font-size:11px;color:var(--text-m);font-weight:600;">Target</label><input type="text" id="tal-form-tgt" placeholder="Target..." style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;"></div>';
  html+='<div><label style="font-size:11px;color:var(--text-m);font-weight:600;">Bobot (%)</label><input type="number" id="tal-form-bbt" min="0.01" max="100" step="0.01" placeholder="%" style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;"></div>';
  html+='<div><label style="font-size:11px;color:var(--text-m);font-weight:600;">Progress (%)</label><input type="number" id="tal-form-prg" min="0" max="100" step="0.01" placeholder="%" style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;"></div>';
  html+='</div>';
  html+='<div style="margin-bottom:12px;"><label style="font-size:11px;color:var(--text-m);font-weight:600;">Review Atasan</label><input type="text" id="tal-form-rvw" placeholder="Review atasan..." style="width:100%;padding:7px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;margin-top:4px;box-sizing:border-box;"></div>';
  html+='<div style="display:flex;gap:8px;">';
  html+='<button onclick="talFormSave()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 20px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2713; Simpan</button>';
  html+='<button onclick="talFormCancel()" style="background:none;border:1.5px solid var(--border);color:var(--text-m);border-radius:var(--radius-sm);padding:7px 14px;cursor:pointer;font-size:13px;font-family:var(--font);">&#x2715; Batal</button>';
  html+='</div></div>';

  // Top action bar
  if(isOwnerOrAdmin()){
    html+='<div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">';
    html+='<button onclick="talOpenAddForm()" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);font-weight:600;">&#x2795; Tambah TAL</button>';
    if(moduleEmpty){
      html+='<button onclick="talDupModuleAll()" style="background:none;border:1.5px solid var(--border);color:var(--text);border-radius:var(--radius-sm);padding:7px 16px;cursor:pointer;font-size:13px;font-family:var(--font);">&#x1F4CB; Duplikat Bulan Lalu</button>';
    }
    html+='</div>';
  }

  // Only render cards for divisions that have data
  var hasAny=false;
  divsToShow.forEach(function(d){
    var rows=(_talG(d,talYear,talMonth).rows||[]);
    if(rows.length>0){
      hasAny=true;
      html+=talBuildDivCard(d,talYear,talMonth);
    }
  });

  // Empty state
  if(!hasAny){
    html+='<div style="text-align:center;padding:60px 24px;color:var(--text-l);">';
    html+='<div style="font-size:48px;margin-bottom:16px;">&#x1F4CB;</div>';
    html+='<div style="font-size:18px;font-weight:700;color:var(--text);margin-bottom:8px;">Belum ada TAL</div>';
    html+='<div style="font-size:13px;">Klik <strong>&#x2795; Tambah TAL</strong> untuk menambahkan TAL baru';
    if(isOwnerOrAdmin()) html+=' atau <strong>&#x1F4CB; Duplikat Bulan Lalu</strong> jika sudah ada data bulan lalu.';
    html+='</div></div>';
  }

  wrap.innerHTML=html;
}

function talBuildDivCard(d,y,m){
  var data=_talG(d,y,m);var rows=data.rows||[];
  var saved=rows.filter(function(r){return !r.editing&&r.tal;});
  var total=talTotalScore(d,y,m);
  var totalBobot=saved.reduce(function(acc,r){return acc+(r.bobot||0);},0);
  var anyEditing=rows.some(function(r){return r.editing;});

  var h='<div class="card" style="margin-bottom:16px;padding:0;overflow:hidden;">';

  // Card header (like OKR style)
  h+='<div style="background:var(--primary);padding:11px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">';
  h+='<span style="font-size:15px;font-weight:800;color:#fff;letter-spacing:.5px;">&#x1F4CB; '+okrEsc(TAL_DIV_NAMES[d])+'</span>';
  h+='<div style="display:flex;align-items:center;gap:8px;">';
  if(saved.length>0){
    h+='<span class="'+scoreClass(total)+'" style="font-size:15px;font-weight:800;background:rgba(255,255,255,.18);padding:3px 12px;border-radius:20px;">'+total.toFixed(2)+'</span>';
  }
  if(isOwnerOrAdmin()){
    if(!anyEditing){
      h+='<button onclick="talEditAllRows('+d+')" style="background:rgba(255,255,255,.15);border:1.5px solid rgba(255,255,255,.4);color:#fff;border-radius:var(--radius-sm);padding:4px 12px;cursor:pointer;font-size:12px;font-family:var(--font);font-weight:600;">&#x270F;&#xFE0F; Edit TAL</button>';
    }else{
      h+='<button onclick="talCancelAllEdits('+d+')" style="background:rgba(255,255,255,.1);border:1.5px solid rgba(255,255,255,.3);color:#fff;border-radius:var(--radius-sm);padding:4px 12px;cursor:pointer;font-size:12px;font-family:var(--font);">&#x2715; Batal Edit</button>';
    }
    h+='<button onclick="talDeleteDiv('+d+')" style="background:rgba(220,38,38,.7);border:1.5px solid rgba(255,255,255,.3);color:#fff;border-radius:var(--radius-sm);padding:4px 8px;cursor:pointer;font-size:13px;line-height:1;">&#x1F5D1;</button>';
  }
  h+='</div></div>';

  h+='<div style="padding:16px;">';

  // Score summary banner
  if(saved.length>0){
    h+='<div style="display:flex;align-items:center;gap:16px;padding:10px 14px;background:var(--bg2);border:2px solid var(--primary);border-radius:var(--radius);margin-bottom:12px;flex-wrap:wrap;">';
    h+='<div><div style="font-size:11px;font-weight:600;color:var(--text-m);">SCORE AKHIR</div>';
    h+='<div class="final-big '+scoreClass(total)+'" style="font-size:2rem;">'+total.toFixed(2)+'</div></div>';
    h+='<div style="font-size:12px;color:var(--text-m);">'+saved.length+' TAL &bull; Total bobot: <strong>'+totalBobot+'%</strong></div>';
    h+='</div>';
  }

  h+='<div style="overflow-x:auto;">';
  h+='<table style="width:100%;border-collapse:collapse;font-size:12px;min-width:700px;">';
  h+='<thead><tr style="border-bottom:2px solid var(--border);background:var(--bg);">';
  var hdrs=['No','TAL','Deadline','Target','Progress (%)','Bobot (%)','Score','Review Atasan'];
  if(anyEditing) hdrs.push('Aksi');
  hdrs.forEach(function(hd,i){
    h+='<th style="position:sticky;top:0;text-align:'+(i===0||i>=4?'center':'left')+';padding:9px 10px;color:var(--text-m);font-weight:600;white-space:nowrap;background:var(--bg);border-bottom:2px solid var(--border);">'+hd+'</th>';
  });
  h+='</tr></thead><tbody>';

  rows.forEach(function(row,idx){
    if(row.editing){
      h+='<tr style="background:var(--bg);border-bottom:1px solid var(--border);">';
      h+='<td style="padding:7px 8px;text-align:center;color:var(--text-l);">'+(idx+1)+'</td>';
      h+='<td style="padding:5px 6px;min-width:160px;"><input id="tal-tal-'+d+'-'+idx+'" type="text" value="'+okrEsc(row.tal||'')+'" placeholder="Deskripsi TAL..." style="width:100%;padding:5px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;box-sizing:border-box;"></td>';
      h+='<td style="padding:5px 6px;"><input id="tal-dl-'+d+'-'+idx+'" type="date" value="'+okrEsc(row.deadline||'')+'" style="padding:5px 6px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;"></td>';
      h+='<td style="padding:5px 6px;min-width:110px;"><input id="tal-tgt-'+d+'-'+idx+'" type="text" value="'+okrEsc(row.target||'')+'" placeholder="Target..." style="width:100%;padding:5px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;box-sizing:border-box;"></td>';
      h+='<td style="padding:5px 6px;text-align:center;"><input id="tal-prg-'+d+'-'+idx+'" type="number" min="0" max="100" step="0.01" value="'+(row.progress!==null&&row.progress!==undefined?row.progress:'')+'" placeholder="%" style="width:65px;padding:5px 6px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;text-align:center;"></td>';
      h+='<td style="padding:5px 6px;text-align:center;"><input id="tal-bbt-'+d+'-'+idx+'" type="number" min="0.01" max="100" step="0.01" value="'+(row.bobot!==null&&row.bobot!==undefined?row.bobot:'')+'" placeholder="%" style="width:58px;padding:5px 6px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;text-align:center;"></td>';
      h+='<td style="padding:5px 6px;text-align:center;color:var(--text-l);">?</td>';
      h+='<td style="padding:5px 6px;"><input id="tal-rvw-'+d+'-'+idx+'" type="text" value="'+okrEsc(row.review||'')+'" placeholder="Review atasan..." style="width:100%;padding:5px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;box-sizing:border-box;"></td>';
      h+='<td style="padding:5px 6px;text-align:center;white-space:nowrap;">';
      h+='<button onclick="talSaveRow('+d+','+idx+')" style="background:var(--primary);border:none;color:#fff;border-radius:var(--radius-sm);padding:5px 10px;cursor:pointer;font-size:11px;font-family:var(--font);font-weight:600;">&#x2713;</button> ';
      h+='<button onclick="talDeleteRow('+d+','+idx+')" style="background:none;border:1.5px solid #fca5a5;color:#dc2626;border-radius:var(--radius-sm);padding:5px 8px;cursor:pointer;font-size:11px;font-family:var(--font);">&#x1F5D1;</button>';
      h+='</td></tr>';
    }else{
      var sc=talRowScore(row);
      var hasPrg=row.progress!==null&&row.progress!==undefined&&row.progress!=='';
      h+='<tr style="border-bottom:1px solid var(--border);">';
      h+='<td style="padding:8px 10px;text-align:center;color:var(--text-l);">'+(idx+1)+'</td>';
      h+='<td style="padding:8px 10px;font-weight:600;color:var(--text);">'+okrEsc(row.tal||'?')+'</td>';
      h+='<td style="padding:8px 10px;white-space:nowrap;font-size:11px;color:var(--text-m);">'+okrEsc(row.deadline||'?')+'</td>';
      h+='<td style="padding:8px 10px;color:var(--text-m);">'+okrEsc(row.target||'?')+'</td>';
      h+='<td style="padding:6px 8px;text-align:center;"><div style="display:inline-flex;align-items:center;gap:4px;">';
      h+='<input id="tal-pli-'+d+'-'+idx+'" type="number" min="0" max="100" step="0.01" value="'+(hasPrg?row.progress:'')+'" placeholder="%" style="width:62px;padding:4px 6px;border:1.5px solid '+(hasPrg?'var(--primary)':'var(--border)')+';border-radius:var(--radius-sm);font-family:var(--font);font-size:12px;text-align:center;">';
      h+='<button onclick="talSaveProgress('+d+','+idx+')" style="background:var(--primary);border:none;color:#fff;border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:12px;line-height:1;display:flex;align-items:center;justify-content:center;flex-shrink:0;">&#x2713;</button>';
      h+='</div></td>';
      h+='<td style="padding:8px 10px;text-align:center;color:var(--text-m);">'+(row.bobot||0)+'%</td>';
      h+='<td style="padding:8px 10px;text-align:center;">';
      if(hasPrg&&row.bobot){h+='<span class="score-num '+scoreClass(parseFloat(row.progress))+'" style="font-size:1rem;font-weight:700;">'+sc.toFixed(2)+'</span>';}
      else{h+='<span style="color:var(--text-l);">?</span>';}
      h+='</td>';
      h+='<td style="padding:6px 8px;"><div style="display:flex;gap:4px;align-items:center;">';
      h+='<input id="tal-rli-'+d+'-'+idx+'" type="text" value="'+okrEsc(row.review||'')+'" placeholder="Review atasan..." style="flex:1;min-width:80px;padding:4px 8px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-family:var(--font);font-size:11px;">';
      h+='<button onclick="talSaveReview('+d+','+idx+')" style="background:none;border:1.5px solid var(--primary);color:var(--primary);border-radius:50%;width:22px;height:22px;cursor:pointer;font-size:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">&#x2713;</button>';
      h+='</div></td>';
      if(anyEditing) h+='<td></td>';
      h+='</tr>';
    }
  });

  h+='<tr style="border-top:2px solid var(--border);background:var(--bg2);">';
  h+='<td colspan="6" style="padding:11px 14px;font-weight:700;font-size:13px;color:var(--text);text-align:right;">&#x1F3AF; Score Akhir &nbsp;=&nbsp; &#x2211; (Progress &times; Bobot / 100)</td>';
  h+='<td style="padding:11px 14px;text-align:center;">';
  if(saved.length>0){h+='<span class="score-num '+scoreClass(total)+'" style="font-size:1.5rem;font-weight:800;">'+total.toFixed(2)+'</span>';}
  else{h+='<span style="color:var(--text-l);">?</span>';}
  h+='</td>';
  var extraCols=anyEditing?2:1;
  h+='<td colspan="'+extraCols+'" style="padding:11px 14px;"></td></tr>';
  h+='</tbody></table></div>';

  h+='</div></div>';
  return h;
}

function talEditAllRows(d){
  var data=_talG(d,talYear,talMonth);
  var rows=data.rows||[];
  rows.forEach(function(r){r.editing=true;});
  _talS(d,talYear,talMonth,data);
  talRender();
}
function talCancelAllEdits(d){
  var data=_talG(d,talYear,talMonth);
  var rows=data.rows||[];
  rows.forEach(function(r){r.editing=false;});
  _talS(d,talYear,talMonth,data);
  talRender();
}
function talDeleteDiv(d){
  if(!confirm('Hapus semua TAL '+TAL_DIV_NAMES[d]+' bulan ini?'))return;
  var data=_talG(d,talYear,talMonth);
  data.rows=[];
  _talS(d,talYear,talMonth,data);
  okrSaveLS();
  talRender();
  notify('TAL '+okrEsc(TAL_DIV_NAMES[d])+' dihapus');
}
function talDupModuleAll(){
  if(!confirm('Duplikat semua TAL dari bulan lalu?'))return;
  var divsToShow=talGetVisibleDivs();
  var y=talYear,m=talMonth;
  var pm=m-1,py=y;if(pm<1){pm=12;py=y-1;}
  var copied=0;
  divsToShow.forEach(function(d){
    var prev=_talG(d,py,pm);
    if(!prev.rows||prev.rows.length===0)return;
    var cur=_talG(d,y,m);
    var newRows=(cur.rows||[]).slice();
    prev.rows.filter(function(r){return !r.editing&&r.tal;}).forEach(function(r){
      newRows.push({tal:r.tal,deadline:r.deadline,target:r.target,bobot:r.bobot,progress:null,review:'',editing:false,savedAt:new Date().toISOString()});
    });
    cur.rows=newRows;
    _talS(d,y,m,cur);
    copied++;
  });
  if(copied===0){notify('Tidak ada data bulan lalu untuk diduplikat.','error');return;}
  okrSaveLS();
  talRender();
  notify('Duplikat dari '+BULS[pm-1]+' '+py+' berhasil ('+copied+' divisi)');
}

"""

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()

    start = c.find('function talRender(){')
    end = c.find('function talOpenAddForm(){')
    if start == -1 or end == -1:
        print('ERROR: boundaries not found in', fpath)
        continue

    c_new = c[:start] + NEW_SECTION + c[end:]

    # Verify
    checks = ['talBuildDivCard', 'talEditAllRows', 'talCancelAllEdits',
              'talDeleteDiv', 'talDupModuleAll', 'moduleEmpty', 'hasAny']
    ok = all(k in c_new for k in checks)

    if ok:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(c_new)
        print(fpath.split('\\')[-1], '- OK, size:', len(c_new))
    else:
        missing = [k for k in checks if k not in c_new]
        print('ERROR missing:', missing, 'in', fpath.split('\\')[-1])
