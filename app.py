from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
import hashlib, hmac, json

app = FastAPI()

class IngestBody(BaseModel):
    device_id: str
    event_type: str
    occurred_at: datetime
    payload: dict

def verify_signature(raw: bytes, sig: str, secret: str) -> bool:
    mac = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig or "")

@app.post("/ingest")
async def ingest(body: IngestBody, x_signature: str | None = Header(default=None)):
    # 1) 서명/토큰 검증
    raw = json.dumps(body.dict(), separators=(",", ":"), default=str).encode()
    if not verify_signature(raw, x_signature or "", secret="device-shared-secret"):
        raise HTTPException(401, "Invalid signature")

    # 2) 아이템포턴시 키 생성
    idem = hashlib.sha1(f"{body.device_id}:{body.occurred_at.isoformat()}:{body.event_type}".encode()).hexdigest()

    # 3) 브로커/큐에 적재 (여기선 단순화하여 즉시 처리한다고 가정)
    risk_score, risk_level, category, top_signals = run_detection(body)
    event_id = save_event(body, risk_score, risk_level, idem)

    incident_id = None
    if risk_level in ("HIGH", "CRITICAL"):
        incident_id = open_or_update_incident(body.device_id, risk_level, category, top_signals)
        enqueue_alerts(incident_id, risk_level)

    return {"ok": True, "risk_level": risk_level, "incident_id": incident_id, "event_id": event_id}
