# Salin file ini menjadi local_config.py lalu isi nilainya.
# local_config.py TIDAK masuk git (sudah ada di .gitignore), jadi kunci rahasia
# Anda tidak akan ikut ter-push ke mana pun.

# ── Supabase (penyimpanan data OKR) ─────────────────────────────
# Dashboard Supabase → Project Settings → API
SUPABASE_URL = 'https://ivxfbpbwwyvkgijrkycj.supabase.co'
SUPABASE_SERVICE_KEY = ''   # kunci "service_role" (bukan "anon")

# ── Backblaze B2 (penyimpanan file: Excel, foto, dokumen) ───────
# Backblaze → App Keys → Add a New Application Key
#   Allow access to Bucket : pinuspackindo-okr   (jangan "All")
#   Type of Access         : Read and Write
B2_KEY_ID = ''
B2_APP_KEY = ''
B2_BUCKET = 'pinuspackindo-okr'
B2_ENDPOINT = 's3.us-east-005.backblazeb2.com'
