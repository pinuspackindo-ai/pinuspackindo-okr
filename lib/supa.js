// Akses Supabase lewat REST (PostgREST) — tanpa dependency.
//
// ENV:
//   SUPABASE_URL              mis. https://ivxfbpbwwyvkgijrkycj.supabase.co
//   SUPABASE_SERVICE_KEY      service_role key (server-side saja, JANGAN di frontend)
//
// Tabel yang dipakai (lihat DOKUMENTASI.md utk SQL-nya):
//   create table okr_state (
//     id text primary key,
//     data jsonb not null default '{}'::jsonb,
//     ts bigint not null default 0,
//     updated_at timestamptz not null default now()
//   );
// Seluruh data OKR disimpan sebagai SATU baris id='main', mengganti okr_data.json.

const TABLE = 'okr_state';
const ROW_ID = 'main';

function cfg() {
  return {
    url: (process.env.SUPABASE_URL || '').replace(/\/+$/, ''),
    key: process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || '',
  };
}

function siap() {
  const c = cfg();
  return !!(c.url && c.key);
}

function headers(extra) {
  const c = cfg();
  return Object.assign({
    'apikey': c.key,
    'Authorization': 'Bearer ' + c.key,
    'Content-Type': 'application/json',
  }, extra || {});
}

/** Ambil seluruh data OKR. Kembalikan {} kalau baris belum ada. */
async function getState() {
  const c = cfg();
  if (!siap()) throw new Error('ENV Supabase belum lengkap (SUPABASE_URL/SUPABASE_SERVICE_KEY)');
  const u = `${c.url}/rest/v1/${TABLE}?id=eq.${ROW_ID}&select=data,ts`;
  const r = await fetch(u, { headers: headers() });
  if (!r.ok) throw new Error('Supabase GET ' + r.status + ': ' + (await r.text()).slice(0, 200));
  const rows = await r.json();
  if (!rows || !rows.length) return {};
  const d = rows[0].data || {};
  if (rows[0].ts && !d._ts) d._ts = Number(rows[0].ts);
  return d;
}

/** Hanya timestamp — dipakai polling ?meta=1 supaya transfer hemat. */
async function getTs() {
  const c = cfg();
  if (!siap()) throw new Error('ENV Supabase belum lengkap');
  const u = `${c.url}/rest/v1/${TABLE}?id=eq.${ROW_ID}&select=ts`;
  const r = await fetch(u, { headers: headers() });
  if (!r.ok) throw new Error('Supabase GET ts ' + r.status);
  const rows = await r.json();
  return rows && rows.length ? Number(rows[0].ts || 0) : 0;
}

/** Tulis seluruh data OKR (upsert baris 'main'). */
async function putState(data) {
  const c = cfg();
  if (!siap()) throw new Error('ENV Supabase belum lengkap');
  const body = [{
    id: ROW_ID,
    data: data,
    ts: Number(data && data._ts ? data._ts : Date.now()),
    updated_at: new Date().toISOString(),
  }];
  const u = `${c.url}/rest/v1/${TABLE}?on_conflict=id`;
  const r = await fetch(u, {
    method: 'POST',
    headers: headers({ 'Prefer': 'resolution=merge-duplicates,return=minimal' }),
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error('Supabase upsert ' + r.status + ': ' + (await r.text()).slice(0, 300));
  return true;
}

module.exports = { getState, getTs, putState, siap, cfg, TABLE, ROW_ID };
