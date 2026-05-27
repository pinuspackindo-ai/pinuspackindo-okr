from flask import Flask, render_template, request, jsonify, send_file, session
import pandas as pd
from io import BytesIO
import re
from datetime import datetime
import uuid
import os
import json
import base64
import threading
import urllib.request
import urllib.error

# ─── GITHUB CONFIG ──────────────────────────────────────────────────────────
# Isi GITHUB_TOKEN dan GITHUB_REPO sekali, lalu restart Flask.
# Data OKR akan otomatis terpush ke GitHub setiap kali disimpan.
GITHUB_TOKEN  = ''                                    # Diisi otomatis dari local_config.py
GITHUB_REPO   = 'pinuspackindo-ai/pinuspackindo-okr'  # Format: "username/nama-repo"
GITHUB_BRANCH = 'main'         # Branch aktif (biasanya main atau master)
GITHUB_FILE   = 'okr_data.json'  # Path file di dalam repo (jangan diubah)
# Token dibaca dari local_config.py (tidak masuk GitHub — aman)
try:
    from local_config import GITHUB_TOKEN as _LC_TOKEN
    if _LC_TOKEN: GITHUB_TOKEN = _LC_TOKEN
except ImportError:
    pass
# ────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = 'pinus_packindo_secret_2025'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# In-memory result store keyed by session ID (single-user local app)
_store: dict = {}

ACC_KEYWORDS = [
    'HPP','SUPPLIER','HARGA','KUANTITI','QTY',
    'SALAH','DISKON','LEBIH','KURANG','TEMPO','TERMIN','NAMA',
]

# ─── HELPERS ─────────────────────────────────────────────────

def sid():
    if 'sid' not in session:
        session['sid'] = str(uuid.uuid4())
    return session['sid']

def store(key, df):
    _store.setdefault(sid(), {})[key] = df

def get_store(key):
    return _store.get(sid(), {}).get(key)

def find_col(df, keywords):
    for kw in keywords:
        kw_c = kw.lower().replace(' ', '').replace('_', '')
        for col in df.columns:
            if kw_c in str(col).lower().replace(' ', '').replace('_', ''):
                return col
    return None

def read_upload(f):
    name = f.filename.lower()
    return pd.read_csv(f) if name.endswith('.csv') else pd.read_excel(f)

def parse_date(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, (int, float)):
        try:
            return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(val) - 2)
        except Exception:
            return None
    s = str(val).strip()
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    try:
        return pd.to_datetime(s).to_pydatetime()
    except Exception:
        return None

def fmt_date(d):
    if d is None:
        return '-'
    try:
        return d.strftime('%d/%m/%Y')
    except Exception:
        return str(d)

def to_xlsx(df, sheet='Data'):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        df.to_excel(w, sheet_name=sheet, index=False)
    buf.seek(0)
    return buf

# ─── GITHUB PUSH ─────────────────────────────────────────────

def _push_github_bg(data_str):
    """Push okr_data.json ke GitHub via Contents API. Dijalankan di background thread."""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    api_url = 'https://api.github.com/repos/{}/contents/{}'.format(GITHUB_REPO, GITHUB_FILE)
    headers = {
        'Authorization': 'token ' + GITHUB_TOKEN,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'User-Agent': 'PINUS-OKR-App',
    }
    # 1. GET SHA file saat ini (wajib untuk update)
    sha = ''
    try:
        req = urllib.request.Request(
            api_url + '?ref=' + GITHUB_BRANCH, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            info = json.loads(resp.read().decode('utf-8'))
            sha = info.get('sha', '')
    except Exception:
        pass  # File belum ada di repo → sha kosong → create baru
    # 2. PUT update / create file
    payload = {
        'message': 'chore: update OKR data',
        'content': base64.b64encode(data_str.encode('utf-8')).decode('ascii'),
        'branch':  GITHUB_BRANCH,
    }
    if sha:
        payload['sha'] = sha
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    try:
        req = urllib.request.Request(api_url, data=body, headers=headers, method='PUT')
        with urllib.request.urlopen(req, timeout=15) as resp:
            print('[GitHub] Push OK — status', resp.status)
    except urllib.error.HTTPError as e:
        print('[GitHub] HTTPError', e.code, e.reason, e.read().decode())
    except Exception as e:
        print('[GitHub] Push error:', e)

# ─── ROUTES ──────────────────────────────────────────────────

OKR_DATA_PATH = os.path.join(os.path.dirname(__file__), 'okr_data.json')

@app.route('/')
def index():
    return render_template('index.html')

# ── OKR Cloud Sync ───────────────────────────────────────────
@app.route('/okr_data.json')
def okr_data_get():
    """Serve okr_data.json — used by frontend to load cross-browser data."""
    if os.path.exists(OKR_DATA_PATH):
        with open(OKR_DATA_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route('/api/okr', methods=['GET', 'POST'])
def okr_api():
    """GET: baca okr_data.json | POST: simpan + push ke GitHub."""
    if request.method == 'GET':
        if os.path.exists(OKR_DATA_PATH):
            with open(OKR_DATA_PATH, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        return jsonify({})
    # POST
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'ok': False, 'msg': 'Invalid data'}), 400
    data_str = json.dumps(data, ensure_ascii=False, indent=2)
    with open(OKR_DATA_PATH, 'w', encoding='utf-8') as f:
        f.write(data_str)
    if GITHUB_TOKEN and GITHUB_REPO:
        threading.Thread(target=_push_github_bg, args=(data_str,), daemon=True).start()
    return jsonify({'ok': True, 'github': bool(GITHUB_TOKEN and GITHUB_REPO)})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if data.get('password') == '010101':
        session['auth'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'msg': 'Password salah. Coba lagi.'})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

# ── Analisa Instock ──────────────────────────────────────────
@app.route('/analyze/instock', methods=['POST'])
def analyze_instock():
    if not session.get('auth'):
        return jsonify({'error': 'Unauthorized'}), 401

    f1 = request.files.get('file1')
    f2 = request.files.get('file2')
    if not f1 or not f2:
        return jsonify({'error': 'Upload dua file Excel'}), 400

    try:
        d1, d2 = read_upload(f1), read_upload(f2)
    except Exception as e:
        return jsonify({'error': f'Gagal membaca file: {e}'}), 400

    name_k1 = find_col(d1, ['name','nama','product','produk','item'])
    qty_k1  = find_col(d1, ['quantityonhand','qtyonhand','onhand','quantity','qty','stok','stock'])
    uom_k1  = find_col(d1, ['unitofmeasure','uom','satuan','unit'])
    name_k2 = find_col(d2, ['name','nama','product','produk','item'])
    qty_k2  = find_col(d2, ['quantityonhand','qtyonhand','onhand','quantity','qty','stok','stock'])

    if not name_k1 or not qty_k1:
        return jsonify({'error': f'Kolom tidak ditemukan di Excel 1. Kolom: {list(d1.columns)}'}), 400
    if not name_k2 or not qty_k2:
        return jsonify({'error': f'Kolom tidak ditemukan di Excel 2. Kolom: {list(d2.columns)}'}), 400

    d1[qty_k1] = pd.to_numeric(d1[qty_k1], errors='coerce').fillna(0)
    d2[qty_k2] = pd.to_numeric(d2[qty_k2], errors='coerce').fillna(0)

    g1 = d1.groupby(name_k1)[qty_k1].sum().reset_index().rename(columns={name_k1:'name', qty_k1:'q1'})
    g2 = d2.groupby(name_k2)[qty_k2].sum().reset_index().rename(columns={name_k2:'name', qty_k2:'q2'})
    uom_map = (d1.dropna(subset=[uom_k1]).groupby(name_k1)[uom_k1].first().to_dict() if uom_k1 else {})

    merged = pd.merge(g1, g2, on='name', how='outer').fillna(0)
    merged['total']    = merged['q1'] + merged['q2']
    merged['uom']      = merged['name'].map(uom_map).fillna('-')
    def _is_excluded(name):
        n = str(name).strip().lower()
        if re.match(r'^\((d|l|n)\)', n): return True
        return any(kw in n for kw in [
            'ongkos kirim', 'ongkos  kirim', 'ongkos\tkirim',
            'uang muka', 'voucher', 'sampul juara', 'jasa sablon', '10 l'
        ]) or 'ongkos' in n and 'kirim' in n
    merged['excluded'] = merged['name'].apply(_is_excluded)
    merged = merged.sort_values('total').reset_index(drop=True)

    shared = len(set(g1['name']) & set(g2['name']))
    below  = merged[(merged['total'] <= 0) & (~merged['excluded'])]
    excl   = merged[(merged['total'] <= 0) &  (merged['excluded'])]
    total  = len(merged)
    bc     = len(below)
    score  = (total - bc) / total * 100 if total else 0

    col_map = {'name':'Name','uom':'Unit of Measure','q1':'QoH Excel 1','q2':'QoH Excel 2','total':'Total QoH'}
    store('instock_below', below[['name','uom','q1','q2','total']].round(2).rename(columns=col_map))
    store('instock_all',  merged[['name','uom','q1','q2','total']].round(2).rename(columns=col_map))

    def rows(df):
        return df[['name','uom','q1','q2','total']].round(2).to_dict(orient='records')

    return jsonify({
        'total': total, 'below': bc, 'above': total - bc,
        'shared': shared, 'excluded': len(excl),
        'score': round(score, 1),
        'below_rows': rows(below),
        'all_rows':   merged[['name','uom','q1','q2','total','excluded']].round(2).to_dict(orient='records'),
    })

# ── Analisa Keterlambatan PO ─────────────────────────────────
@app.route('/analyze/late', methods=['POST'])
def analyze_late():
    if not session.get('auth'):
        return jsonify({'error': 'Unauthorized'}), 401

    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'Upload file Excel'}), 400
    try:
        df = read_upload(f)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    ref_k  = find_col(df, ['orderreference','reference','ordref','po','ponumber','order'])
    ord_k  = find_col(df, ['orderdate','orddate','tanggalorder','tglorder','purchasedate'])
    rec_k  = find_col(df, ['receiveddate','receivedate','recdate','tanggalterima','tglterima','received','arrival'])
    prod_k = find_col(df, ['product','produk','item','nama'])

    if not ref_k or not ord_k or not rec_k:
        return jsonify({'error': f'Kolom tidak ditemukan. Tersedia: {list(df.columns)}'}), 400

    rows = []
    for _, row in df.iterrows():
        ref  = str(row.get(ref_k) or '').strip()
        prod = str(row.get(prod_k) or '-').strip() if prod_k else '-'
        od   = parse_date(row.get(ord_k))
        rd   = parse_date(row.get(rec_k))
        late = od and rd and od.date() == rd.date()
        rows.append({'ref': ref, 'product': prod,
                     'order_date': fmt_date(od), 'received_date': fmt_date(rd),
                     'status': 'Terlambat' if late else 'Ontime'})

    df_p = pd.DataFrame(rows)

    ref_map: dict = {}
    for _, r in df_p.iterrows():
        if not r['ref']:
            continue
        if r['ref'] not in ref_map:
            ref_map[r['ref']] = r.to_dict()
        elif r['status'] == 'Terlambat':
            ref_map[r['ref']]['status'] = 'Terlambat'

    uniq  = pd.DataFrame(list(ref_map.values())) if ref_map else pd.DataFrame(columns=df_p.columns)
    late  = uniq[uniq['status'] == 'Terlambat'] if len(uniq) else uniq
    total = len(uniq)
    tlbt  = len(late)
    score = (total - tlbt) / total * 100 if total else 0

    _store.setdefault(sid(), {})['late_score']   = score
    _store[sid()]['total_po_ref'] = total

    col_map = {'ref':'Order Reference','product':'Product',
               'order_date':'Order Date','received_date':'Received Date','status':'Status'}
    store('late_late', late[['ref','order_date','received_date','status']].rename(columns=col_map))
    store('late_all',  df_p.rename(columns=col_map))

    return jsonify({
        'total': total, 'terlambat': tlbt, 'ontime': total - tlbt,
        'score': round(score, 1),
        'late_rows': late[['ref','order_date','received_date','status']].to_dict(orient='records'),
        'all_rows':  df_p.to_dict(orient='records'),
    })

# ── Analisa Akurasi PO ───────────────────────────────────────
@app.route('/analyze/accuracy', methods=['POST'])
def analyze_accuracy():
    if not session.get('auth'):
        return jsonify({'error': 'Unauthorized'}), 401

    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'Upload file Excel'}), 400
    try:
        df = read_upload(f)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    origin_k = find_col(df, ['sourceorigin','source origin'])
    doc_k    = find_col(df, ['sourcedocument','source document'])

    if not origin_k:
        return jsonify({'error': f'Kolom Source Origin tidak ditemukan. Tersedia: {list(df.columns)}'}), 400

    rows = []
    for _, row in df.iterrows():
        origin  = str(row.get(origin_k) or '').strip()
        doc     = str(row.get(doc_k) or '-').strip() if doc_k else '-'
        matched = [kw for kw in ACC_KEYWORDS if kw in origin.upper()]
        rows.append({'doc': doc, 'origin': origin,
                     'status': 'Tidak Akurat' if matched else 'Akurat',
                     'matched': ', '.join(matched)})

    df_acc    = pd.DataFrame(rows)
    inacc     = df_acc[df_acc['status'] == 'Tidak Akurat']
    total_ref = _store.get(sid(), {}).get('total_po_ref') or len(df_acc)
    inacc_cnt = len(inacc)
    acc_cnt   = max(0, total_ref - inacc_cnt)
    score     = acc_cnt / total_ref * 100 if total_ref else 0

    _store.setdefault(sid(), {})['acc_score'] = score
    col_map = {'doc':'Source Document','origin':'Source Origin','status':'Status','matched':'Kata Kunci'}
    store('acc_inacc', inacc.rename(columns=col_map))
    store('acc_all',   df_acc.rename(columns=col_map))

    late_score = _store.get(sid(), {}).get('late_score')
    final = round(late_score * 0.7 + score * 0.3, 1) if late_score is not None else None

    return jsonify({
        'total_ref': total_ref, 'inacc': inacc_cnt, 'acc': acc_cnt,
        'score': round(score, 1), 'final': final,
        'late_score': round(late_score, 1) if late_score is not None else None,
        'inacc_rows': inacc.to_dict(orient='records'),
        'all_rows':   df_acc.to_dict(orient='records'),
    })

# ── Analisa Penerimaan ───────────────────────────────────────
@app.route('/analyze/shipping', methods=['POST'])
def analyze_shipping():
    if not session.get('auth'):
        return jsonify({'error': 'Unauthorized'}), 401

    f = request.files.get('file')
    if not f:
        return jsonify({'error': 'Upload file Excel'}), 400
    try:
        df = read_upload(f)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    ref_k  = find_col(df, ['orderreference','order reference','reference','ordref','po'])
    prod_k = find_col(df, ['product','produk','item','nama'])
    rqty_k = find_col(df, ['receivedqty','received qty','receivedquantity','qty received','qtyreceived','terima'])
    qty_k  = next((c for c in df.columns if c.strip().lower() == 'quantity'), find_col(df, ['quantity']))

    if not rqty_k or not qty_k:
        return jsonify({'error': f'Kolom Received Qty / Quantity tidak ditemukan. Tersedia: {list(df.columns)}'}), 400

    df[rqty_k] = pd.to_numeric(df[rqty_k], errors='coerce').fillna(0)
    df[qty_k]  = pd.to_numeric(df[qty_k],  errors='coerce').fillna(0)

    rows = []
    for _, row in df.iterrows():
        rqty = round(float(row[rqty_k]), 4)
        qty  = round(float(row[qty_k]),  4)
        rows.append({
            'ref':     str(row.get(ref_k)  or '-').strip() if ref_k  else '-',
            'product': str(row.get(prod_k) or '-').strip() if prod_k else '-',
            'received_qty': round(rqty, 2),
            'quantity':     round(qty,  2),
            'status': 'Akurat' if rqty == qty else 'Tidak Akurat',
        })

    df_all   = pd.DataFrame(rows)
    df_inacc = df_all[df_all['status'] == 'Tidak Akurat']
    total    = len(df_all)
    inacc    = len(df_inacc)
    score    = (total - inacc) / total * 100 if total else 0

    col_map = {'ref':'Order Reference','product':'Product',
               'received_qty':'Received Qty','quantity':'Quantity','status':'Status'}
    store('ship_inacc', df_inacc.rename(columns=col_map))
    store('ship_all',   df_all.rename(columns=col_map))

    return jsonify({
        'total': total, 'inacc': inacc, 'acc': total - inacc,
        'score': round(score, 1),
        'inacc_rows': df_inacc.to_dict(orient='records'),
        'all_rows':   df_all.to_dict(orient='records'),
    })

# ── Download ─────────────────────────────────────────────────
DOWNLOAD_NAMES = {
    'instock_below': 'Analisa_Instock_BelowZero.xlsx',
    'instock_all':   'Analisa_Instock_Semua.xlsx',
    'late_late':     'PO_Terlambat.xlsx',
    'late_all':      'PO_Keterlambatan_Semua.xlsx',
    'acc_inacc':     'PO_Tidak_Akurat.xlsx',
    'acc_all':       'PO_Akurasi_Semua.xlsx',
    'ship_inacc':    'Penerimaan_Tidak_Akurat.xlsx',
    'ship_all':      'Penerimaan_Semua.xlsx',
}

@app.route('/download/<key>')
def download(key):
    if not session.get('auth'):
        return 'Unauthorized', 401
    df = get_store(key)
    if df is None:
        return 'Data tidak ditemukan. Jalankan analisa terlebih dahulu.', 404
    filename = DOWNLOAD_NAMES.get(key, f'{key}.xlsx')
    return send_file(
        to_xlsx(df),
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\n  PINUS PACKINDO :: TOOLS ANALISA')
    print('  Buka browser: http://localhost:5000\n')
    app.run(debug=False, port=5000, host='0.0.0.0')
