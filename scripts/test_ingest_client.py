# scripts/test_ingest_client.py
import os, json, hmac, hashlib, requests
from datetime import datetime, timezone
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(ROOT, ".env"))

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
SECRET = os.getenv("DEVICE_HMAC_SECRET", "device-shared-secret")

body = {
    "device_id": "11111111-2222-3333-4444-555555555555",  # ← 실제 등록된 device_id로 바꾸세요!
    "event_type": "intrusion",
    "occurred_at": datetime.now(timezone.utc).isoformat(),
    "payload": {"score": 0.92}
}

# ✅ 공백 없는 JSON을 '한 번' 만들고
payload_json = json.dumps(body, separators=(",", ":"), default=str)
raw = payload_json.encode()

# ✅ 같은 바이트로 서명
sig = hmac.new(SECRET.encode(), raw, hashlib.sha1).hexdigest()
headers = {
    "Content-Type": "application/json",
    "X-Signature": f"sha1={sig}"
}

# ✅ 같은 문자열로 전송
res = requests.post(f"{BASE}/ingest", headers=headers, data=payload_json)

print("STATUS:", res.status_code, "| CT:", res.headers.get("content-type"))
print("BODY  :", res.text)
try:
    print("JSON  :", res.json())
except Exception as e:
    print("JSON parse error ->", e)
