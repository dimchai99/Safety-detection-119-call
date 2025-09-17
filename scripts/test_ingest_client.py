# scripts/test_ingest_client.py
import os, json, hmac, hashlib, requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# ✅ 프로젝트 루트의 .env를 확실히 로드
ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(ROOT, ".env"))

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
SECRET = os.getenv("DEVICE_HMAC_SECRET", "device-shared-secret")

body = {
    "device_id": "11111111-2222-3333-4444-555555555555",
    "event_type": "intrusion",
    "occurred_at": datetime.now(timezone.utc).isoformat(),
    "payload": {"score": 0.92}
}
raw = json.dumps(body, separators=(",", ":"), default=str).encode()
sig = hmac.new(SECRET.encode(), raw, hashlib.sha1).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-Signature": f"sha1={sig}"
}

res = requests.post(f"{BASE}/ingest", headers=headers, data=json.dumps(body))

# ✅ 디버그 출력 강화 (무슨 응답인지 먼저 확인)
print("STATUS:", res.status_code, "| CT:", res.headers.get("content-type"))
print("BODY  :", res.text)
try:
    print("JSON  :", res.json())
except Exception as e:
    print("JSON parse error ->", e)
