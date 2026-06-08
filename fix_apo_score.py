"""
Fix score Akurasi PO Mei 2026 di cloud (okr_data.json → data branch).
Score sebelumnya 83.3% — zeroed oleh recovery script sebelumnya.
"""
import json, base64, urllib.request, urllib.parse

try:
    from local_config import GITHUB_TOKEN
except ImportError:
    raise SystemExit("ERROR: local_config.py tidak ditemukan atau GITHUB_TOKEN tidak ada.")

REPO   = "pinuspackindo-ai/pinuspackindo-okr"
BRANCH = "data"
FILE   = "okr_data.json"
API    = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "PINUS-OKR-fix",
    "Content-Type": "application/json",
}

def gh_get(url, headers, raw=False):
    req = urllib.request.Request(url, headers={**headers, "Accept": "application/vnd.github.raw" if raw else "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req) as r:
        return r.read()

def gh_put(url, headers, body_dict, sha):
    content_b64 = base64.b64encode(json.dumps(body_dict, ensure_ascii=False, indent=2).encode()).decode()
    payload = json.dumps({
        "message": "fix: restore Akurasi PO Mei score 83.3% [vercel skip]",
        "content": content_b64,
        "branch": BRANCH,
        "sha": sha,
    }).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# 1. GET current data + SHA
print("Fetching current okr_data.json ...")
meta = json.loads(gh_get(f"{API}?ref={BRANCH}", HEADERS))
sha = meta["sha"]
data = json.loads(base64.b64decode(meta["content"]).decode())
print(f"  SHA: {sha}")

# 2. Tampilkan nilai saat ini
apo = data.get("_p_apo_2026_05", {})
print(f"\n[SEBELUM] _p_apo_2026_05:")
print(f"  finalScore  = {apo.get('finalScore')}")
print(f"  lateScore   = {apo.get('lateScore')}")
print(f"  accScore    = {apo.get('accScore')}")
purch_rows = data.get("2026-05", {}).get("Purchasing", {}).get("rows", [])
for r in purch_rows:
    if "akurasi" in r.get("keyResult","").lower():
        print(f"\n[SEBELUM] OKR Purchasing Akurasi PO actual = {r.get('actual')}")

# 3. Tanya user score yang benar
print("\nScore Akurasi PO Mei yang benar (tekan Enter = gunakan 83.3):")
inp = input("Score: ").strip()
score = float(inp) if inp else 83.3
print(f"Akan set score = {score}")

# 4. Update _p_apo_2026_05
data["_p_apo_2026_05"]["finalScore"] = score
data["_p_apo_2026_05"]["lateScore"]  = score
data["_p_apo_2026_05"]["accScore"]   = score
data["_p_apo_2026_05"]["score"]      = score   # field tambahan buat render

# 5. Update OKR dashboard Purchasing → Akurasi PO
updated_okr = False
for r in data.get("2026-05", {}).get("Purchasing", {}).get("rows", []):
    if "akurasi" in r.get("keyResult","").lower():
        r["actual"] = score
        updated_okr = True
        print(f"  ✓ OKR actual diupdate ke {score}")

# 6. PUT ke GitHub
print("\nPushing ke GitHub ...")
result = gh_put(API, HEADERS, data, sha)
print(f"  Status: {result.get('content',{}).get('name','?')} — OK")

print(f"\n✅ Score Akurasi PO Mei {score}% berhasil diupdate di cloud.")
if not updated_okr:
    print("  ⚠️  OKR row Purchasing Akurasi PO tidak ditemukan — cek manual.")
