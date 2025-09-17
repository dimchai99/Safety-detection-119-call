# app.py (Flask + SQLAlchemy, Supabase Postgres)
import os
import uuid
import json
import hmac
import hashlib
from typing import Tuple, Dict, Any, Optional
from datetime import datetime, timezone

from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from dotenv import load_dotenv

from models.models import Base, User, Device, Event, Incident, Alert, Confirmation, Escalation, Rule, AuditLog

# -----------------------------
# ENV & Flask/DB 초기화
# -----------------------------
load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    raise RuntimeError("SUPABASE_DB_URL not set")

DEVICE_SHARED_SECRET = os.getenv("DEVICE_HMAC_SECRET", "device-shared-secret")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# -----------------------------
# 유틸
# -----------------------------
def utcnow():
    return datetime.now(timezone.utc)

def verify_signature(raw: bytes, signature: str, secret: str) -> bool:
    """
    X-Signature: 'sha1=<hex>' 형태 가정.
    디바이스 측은 동일한 raw(body-json)으로 HMAC-SHA1 생성해서 전송.
    """
    if not signature:
        return False
    sig = signature.split("=", 1)[-1] if "=" in signature else signature
    mac = hmac.new(secret.encode(), msg=raw, digestmod=hashlib.sha1).hexdigest()
    return hmac.compare_digest(mac, sig)

# -----------------------------
# 탐지/저장 파이프라인 함수
# -----------------------------
def run_detection(body: Dict[str, Any]) -> Tuple[float, str, str, Dict[str, Any]]:
    payload = body.get("payload") or {}
    score = payload.get("score")
    level = payload.get("level")
    category = payload.get("category", "generic")

    if score is None:
        et = body.get("event_type") or "unknown"
        score = {"intrusion": 0.9, "motion": 0.7, "tamper": 0.6}.get(et, 0.4)

    if not level:
        if score >= 0.85:
            level = "CRITICAL"
        elif score >= 0.7:
            level = "HIGH"
        elif score >= 0.5:
            level = "MEDIUM"
        else:
            level = "LOW"

    top_signals = {"heuristic": "demo", "inputs": {"event_type": body.get("event_type")}}
    return float(score), str(level), str(category), top_signals

def save_event(body: Dict[str, Any], risk_score: float, risk_level: str, idx_idem: Optional[str]) -> int:
    if idx_idem:
        existing = db.session.execute(
            select(Event).where(Event.idx_idempotency == idx_idem)
        ).scalar_one_or_none()
        if existing:
            return existing.id

    evt = Event(
        device_id=body.get("device_id"),
        event_type=body.get("event_type"),
        payload=body.get("payload"),
        risk_score=risk_score,
        risk_level=risk_level,
        occurred_at=utcnow(),   # 필요 시 body의 occurred_at parse 반영
        received_at=utcnow(),
        idx_idempotency=idx_idem,
    )
    db.session.add(evt)
    db.session.commit()
    return evt.id

def open_or_update_incident(device_id: str, risk_level: str, category: Optional[str] = None,
                            top_signals: Optional[Dict[str, Any]] = None) -> str:
    inc = db.session.execute(
        select(Incident).where(
            Incident.device_id == device_id,
            Incident.status == "open",
        ).order_by(Incident.opened_at.desc())
    ).scalar_one_or_none()

    def rank(x: str) -> int:
        order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        return order.get((x or "").upper(), 0)

    if inc:
        if rank(risk_level) > rank(inc.risk_level or ""):
            inc.risk_level = risk_level
        if category:
            inc.category = category
        if top_signals:
            inc.top_signals = top_signals
        db.session.commit()
        return str(inc.id)

    new_inc = Incident(
        id=uuid.uuid4(),
        device_id=device_id,
        status="open",
        category=category,
        risk_level=risk_level,
        top_signals=top_signals,
        opened_at=utcnow(),
    )
    db.session.add(new_inc)
    db.session.commit()
    return str(new_inc.id)

def enqueue_alerts(incident_id: str, risk_level: str, channel: str = "sms", target: Optional[str] = None) -> int:
    a = Alert(
        incident_id=uuid.UUID(incident_id),
        channel=channel,
        target=target or "ops-team",
        payload={"risk_level": risk_level},
        status="queued",
        error=None,
        created_at=utcnow(),
    )
    db.session.add(a)
    db.session.commit()
    return a.id

# -----------------------------
# 라우트
# -----------------------------
@app.get("/")
def health():
    return {"ok": True}

@app.post("/ingest")
def ingest():
    # 1) 서명/토큰 검증
    body = request.get_json(force=True) or {}
    raw = json.dumps(body, separators=(",", ":"), default=str).encode()
    x_signature = request.headers.get("X-Signature", "")
    if not verify_signature(raw, x_signature, DEVICE_SHARED_SECRET):
        abort(401, description="Invalid signature")

    # 2) 멱등 키 생성 (device_id + occurred_at + event_type)
    device_id = body.get("device_id")
    occurred_at = body.get("occurred_at")  # ISO 문자열 기대
    event_type = body.get("event_type")
    idem = hashlib.sha1(f"{device_id}:{occurred_at}:{event_type}".encode()).hexdigest()

    # 3) 처리
    risk_score, risk_level, category, top_signals = run_detection(body)
    event_id = save_event(body, risk_score, risk_level, idem)

    incident_id = None
    if risk_level.upper() in ("HIGH", "CRITICAL"):
        incident_id = open_or_update_incident(device_id, risk_level, category, top_signals)
        enqueue_alerts(incident_id, risk_level)

    return {
        "ok": True,
        "risk_level": risk_level,
        "incident_id": incident_id,
        "event_id": event_id,
    }, 201

@app.post("/users")
def create_user():
    data = request.get_json(force=True) or {}
    email = data.get("email")
    role  = data.get("role", "user")
    nickname = data.get("nickname")
    phone = data.get("phone")

    if not email:
        return {"error": "email required"}, 400

    u = User(
        id=uuid.uuid4(),  # 생략해도 DB default(gen_random_uuid())
        email=email,
        role=role,
        nickname=nickname,
        phone=phone,
        created_at=utcnow(),
    )
    db.session.add(u)
    db.session.commit()
    return {"id": str(u.id), "email": u.email, "role": u.role}, 201

@app.post("/devices")
def register_device():
    data = request.get_json(force=True) or {}
    d = Device(
        id=uuid.uuid4(),
        owner_id=data.get("owner_id"),
        name=data.get("name"),
        type=data.get("type"),
        serial=data.get("serial"),
        location=data.get("location"),
        is_active=True,
        created_at=utcnow(),
    )
    db.session.add(d)
    db.session.commit()
    return {"id": str(d.id), "serial": d.serial}, 201

@app.post("/events")
def ingest_event():
    data = request.get_json(force=True) or {}
    idx_idem = data.get("idx_idempotency")

    if idx_idem:
        existing = db.session.query(Event).filter_by(idx_idempotency=idx_idem).first()
        if existing:
            return {"id": existing.id, "status": "duplicate"}, 200

    evt = Event(
        device_id=data.get("device_id"),
        event_type=data.get("event_type"),
        payload=data.get("payload"),
        risk_score=data.get("risk_score"),
        risk_level=data.get("risk_level"),
        occurred_at=datetime.fromisoformat(data.get("occurred_at")) if data.get("occurred_at") else utcnow(),
        received_at=utcnow(),
        idx_idempotency=idx_idem,
    )
    db.session.add(evt)
    db.session.commit()
    return {"id": evt.id}, 201

@app.post("/incidents")
def open_incident():
    data = request.get_json(force=True) or {}
    inc = Incident(
        id=uuid.uuid4(),
        device_id=data.get("device_id"),
        status="open",
        category=data.get("category"),
        risk_level=data.get("risk_level"),
        top_signals=data.get("top_signals"),
        opened_at=utcnow(),
    )
    db.session.add(inc)
    db.session.commit()
    return {"id": str(inc.id), "status": inc.status}, 201

@app.post("/incidents/<uuid:incident_id>/status")
def update_incident_status(incident_id):
    data = request.get_json(force=True) or {}
    status = data.get("status")
    if status not in {"open", "acknowledged", "closed"}:
        return {"error": "invalid status"}, 400

    inc = db.session.get(Incident, incident_id)
    if not inc:
        return {"error": "not_found"}, 404

    inc.status = status
    if status == "acknowledged":
        inc.acknowledged_at = utcnow()
    elif status == "closed":
        inc.closed_at = utcnow()
    db.session.commit()
    return {"id": str(inc.id), "status": inc.status}, 200

@app.post("/alerts")
def create_alert():
    data = request.get_json(force=True) or {}
    a = Alert(
        incident_id=data.get("incident_id"),
        channel=data.get("channel"),
        target=data.get("target"),
        payload=data.get("payload"),
        status=data.get("status", "queued"),
        error=data.get("error"),
        created_at=utcnow(),
    )
    db.session.add(a)
    db.session.commit()
    return {"id": a.id, "status": a.status}, 201

@app.post("/confirmations")
def confirm_decision():
    data = request.get_json(force=True) or {}
    c = Confirmation(
        incident_id=data.get("incident_id"),
        actor_id=data.get("actor_id"),
        decision=data.get("decision"),
        reason=data.get("reason"),
        decided_at=utcnow(),
    )
    db.session.add(c)
    db.session.commit()
    return {"id": c.id, "decision": c.decision}, 201

@app.get("/incidents/by-device/<uuid:device_id>")
def list_incidents_by_device(device_id):
    q = (
        db.session.query(Incident)
        .filter(Incident.device_id == device_id)
        .order_by(Incident.opened_at.desc())
        .limit(50)
    )
    data = [
        {
            "id": str(x.id),
            "status": x.status,
            "category": x.category,
            "risk_level": x.risk_level,
            "opened_at": x.opened_at.isoformat() if x.opened_at else None,
        }
        for x in q
    ]
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
