# main.py — FastAPI + SQLAlchemy (Supabase Postgres)
import os
import uuid
import json
import hmac
import hashlib
from typing import Tuple, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID

from fastapi import FastAPI, HTTPException, Header, Depends, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

# 너의 모델 모듈 경로 유지
from models.models import Base, User, Device, Event, Incident, Alert, Confirmation, Escalation, Rule, AuditLog

# -----------------------------
# ENV & DB 초기화
# -----------------------------
load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")
if not DB_URL:
    raise RuntimeError("SUPABASE_DB_URL not set")

DEVICE_SHARED_SECRET = os.getenv("DEVICE_HMAC_SECRET", "device-shared-secret")

# Supabase 권장: pool_pre_ping=True
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------
# FastAPI 앱
# -----------------------------
app = FastAPI(title="Safety Detection API (FastAPI)")

# -----------------------------
# 공용 유틸
# -----------------------------
def utcnow():
    return datetime.now(timezone.utc)

def verify_signature(raw: bytes, signature: str | None, secret: str) -> bool:
    """
    X-Signature: 'sha1=<hex>' 형태 가정. raw는 요청 원문 바이트.
    """
    if not signature:
        return False
    sig = signature.split("=", 1)[-1] if "=" in signature else signature
    mac = hmac.new(secret.encode(), msg=raw, digestmod=hashlib.sha1).hexdigest()
    return hmac.compare_digest(mac, sig)

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# 탐지/저장 파이프라인 함수들
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

def save_event(db: Session, body: Dict[str, Any], risk_score: float, risk_level: str, idx_idem: Optional[str]) -> int:
    if idx_idem:
        existing = db.execute(
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
        occurred_at=body.get("occurred_at") or utcnow(),
        received_at=utcnow(),
        idx_idempotency=idx_idem,
    )
    db.add(evt)
    db.commit()
    return evt.id

def open_or_update_incident(db: Session, device_id: str, risk_level: str,
                            category: Optional[str] = None,
                            top_signals: Optional[Dict[str, Any]] = None) -> str:
    inc = db.execute(
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
        db.commit()
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
    db.add(new_inc)
    db.commit()
    return str(new_inc.id)

def enqueue_alerts(db: Session, incident_id: str, risk_level: str,
                   channel: str = "sms", target: Optional[str] = None) -> int:
    a = Alert(
        incident_id=uuid.UUID(incident_id),
        channel=channel,
        target=target or "ops-team",
        payload={"risk_level": risk_level},
        status="queued",
        error=None,
        created_at=utcnow(),
    )
    db.add(a)
    db.commit()
    return a.id

# -----------------------------
# Pydantic 스키마 (요청 바디)
# -----------------------------
class UserCreate(BaseModel):
    email: str
    role: str | None = "user"
    nickname: str | None = None
    phone: str | None = None

class DeviceCreate(BaseModel):
    owner_id: UUID | None = None
    name: str | None = None
    type: str | None = None
    serial: str | None = None
    location: Dict[str, Any] | None = None

class EventIngest(BaseModel):
    device_id: UUID
    event_type: str
    occurred_at: datetime | None = None
    payload: Dict[str, Any] | None = None
    idx_idempotency: str | None = None
    risk_score: float | None = None
    risk_level: str | None = None

class IncidentCreate(BaseModel):
    device_id: UUID
    category: str | None = None
    risk_level: str | None = None
    top_signals: Dict[str, Any] | None = None

class IncidentStatusUpdate(BaseModel):
    status: str  # "open" | "acknowledged" | "closed"

class AlertCreate(BaseModel):
    incident_id: UUID
    channel: str | None = None
    target: str | None = None
    payload: Dict[str, Any] | None = None
    status: str | None = "queued"
    error: str | None = None

class ConfirmationCreate(BaseModel):
    incident_id: UUID
    actor_id: UUID
    decision: str | None = None
    reason: str | None = None

# -----------------------------
# 라우트
# -----------------------------
@app.get("/")
def health():
    return {"ok": True}

@app.post("/ingest", status_code=201)
async def ingest(
    request: Request,
    body: EventIngest,
    x_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # 1) 서명 검증 (요청 원문 바이트 그대로)
    raw = await request.body()
    if not verify_signature(raw, x_signature, DEVICE_SHARED_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2) device 존재 확인
    exists = db.execute(select(Device.id).where(Device.id == str(body.device_id))).scalar_one_or_none()
    if not exists:
        raise HTTPException(status_code=400, detail="unknown device_id")

    # 3) 멱등 키 생성 (없으면 생성)
    occurred_iso = (body.occurred_at or utcnow()).isoformat()
    idem = body.idx_idempotency or hashlib.sha1(
        f"{body.device_id}:{occurred_iso}:{body.event_type}".encode()
    ).hexdigest()

    # 4) 처리
    bdict = body.model_dump()
    # save_event에서 occurred_at을 사용하므로 문자열 대신 datetime을 넘김
    bdict["occurred_at"] = body.occurred_at or utcnow()

    risk_score, risk_level, category, top_signals = run_detection(bdict)
    event_id = save_event(db, bdict, risk_score, risk_level, idem)

    incident_id = None
    if risk_level.upper() in ("HIGH", "CRITICAL"):
        incident_id = open_or_update_incident(
            db, str(body.device_id), risk_level, category, top_signals
        )
        enqueue_alerts(db, incident_id, risk_level)

    return {"ok": True, "risk_level": risk_level, "incident_id": incident_id, "event_id": event_id}

@app.post("/users", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    u = User(
        id=uuid.uuid4(),
        email=payload.email,
        role=payload.role or "user",
        nickname=payload.nickname,
        phone=payload.phone,
        created_at=utcnow(),
    )
    db.add(u)
    db.commit()
    return {"id": str(u.id), "email": u.email, "role": u.role}

@app.post("/devices", status_code=201)
def register_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    if payload.serial:
        exists = db.query(Device).filter_by(serial=payload.serial).first()
        if exists:
            raise HTTPException(status_code=409, detail="serial_already_exists")

    d = Device(
        id=uuid.uuid4(),
        owner_id=str(payload.owner_id) if payload.owner_id else None,
        name=payload.name,
        type=payload.type,
        serial=payload.serial,
        location=payload.location,
        is_active=True,
        created_at=utcnow(),
    )
    db.add(d)
    db.commit()
    return {"id": str(d.id), "serial": d.serial}

@app.get("/devices")
def list_devices(
    owner_id: UUID | None = Query(default=None),
    serial: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Device)
    if owner_id:
        q = q.filter(Device.owner_id == str(owner_id))
    if serial:
        q = q.filter(Device.serial == serial)
    q = q.order_by(Device.created_at.desc()).limit(limit)

    data = [{
        "id": str(d.id),
        "owner_id": str(d.owner_id) if d.owner_id else None,
        "name": d.name,
        "type": d.type,
        "serial": d.serial,
        "location": d.location,
        "is_active": d.is_active,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    } for d in q]
    return data

@app.get("/devices/{device_id}")
def get_device(device_id: UUID, db: Session = Depends(get_db)):
    d = db.get(Device, str(device_id))
    if not d:
        raise HTTPException(status_code=404, detail="not_found")
    return {
        "id": str(d.id),
        "owner_id": str(d.owner_id) if d.owner_id else None,
        "name": d.name,
        "type": d.type,
        "serial": d.serial,
        "location": d.location,
        "is_active": d.is_active,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }

@app.post("/events", status_code=201)
def ingest_event(payload: EventIngest, db: Session = Depends(get_db)):
    idx_idem = payload.idx_idempotency
    if idx_idem:
        existing = db.query(Event).filter_by(idx_idempotency=idx_idem).first()
        if existing:
            return {"id": existing.id, "status": "duplicate"}

    evt = Event(
        device_id=str(payload.device_id),
        event_type=payload.event_type,
        payload=payload.payload,
        risk_score=payload.risk_score,
        risk_level=payload.risk_level,
        occurred_at=payload.occurred_at or utcnow(),
        received_at=utcnow(),
        idx_idempotency=idx_idem,
    )
    db.add(evt)
    db.commit()
    return {"id": evt.id}

@app.post("/incidents", status_code=201)
def open_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    inc = Incident(
        id=uuid.uuid4(),
        device_id=str(payload.device_id),
        status="open",
        category=payload.category,
        risk_level=payload.risk_level,
        top_signals=payload.top_signals,
        opened_at=utcnow(),
    )
    db.add(inc)
    db.commit()
    return {"id": str(inc.id), "status": inc.status}

@app.post("/incidents/{incident_id}/status")
def update_incident_status(incident_id: UUID, payload: IncidentStatusUpdate, db: Session = Depends(get_db)):
    status = payload.status
    if status not in {"open", "acknowledged", "closed"}:
        raise HTTPException(status_code=400, detail="invalid status")

    inc = db.get(Incident, str(incident_id))
    if not inc:
        raise HTTPException(status_code=404, detail="not_found")

    inc.status = status
    if status == "acknowledged":
        inc.acknowledged_at = utcnow()
    elif status == "closed":
        inc.closed_at = utcnow()
    db.commit()
    return {"id": str(inc.id), "status": inc.status}

@app.post("/alerts", status_code=201)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    a = Alert(
        incident_id=str(payload.incident_id),
        channel=payload.channel,
        target=payload.target,
        payload=payload.payload,
        status=payload.status or "queued",
        error=payload.error,
        created_at=utcnow(),
    )
    db.add(a)
    db.commit()
    return {"id": a.id, "status": a.status}

@app.post("/confirmations", status_code=201)
def confirm_decision(payload: ConfirmationCreate, db: Session = Depends(get_db)):
    c = Confirmation(
        incident_id=str(payload.incident_id),
        actor_id=str(payload.actor_id),
        decision=payload.decision,
        reason=payload.reason,
        decided_at=utcnow(),
    )
    db.add(c)
    db.commit()
    return {"id": c.id, "decision": c.decision}

@app.get("/incidents/by-device/{device_id}")
def list_incidents_by_device(device_id: UUID, db: Session = Depends(get_db)):
    q = (
        db.query(Incident)
        .filter(Incident.device_id == str(device_id))
        .order_by(Incident.opened_at.desc())
        .limit(50)
    )
    data = [{
        "id": str(x.id),
        "status": x.status,
        "category": x.category,
        "risk_level": x.risk_level,
        "opened_at": x.opened_at.isoformat() if x.opened_at else None,
    } for x in q]
    return data

# -----------------------------
# 전역 예외 핸들러 (JSON 고정)
# -----------------------------
from sqlalchemy.exc import IntegrityError

@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    # FK/UNIQUE 위반 등
    return JSONResponse(status_code=400, content={"ok": False, "error": "Database integrity error"})

@app.exception_handler(Exception)
def handle_exception(request: Request, exc: Exception):
    # 상세 로그는 서버 콘솔에
    print("UNHANDLED:", repr(exc))
    return JSONResponse(status_code=500, content={"ok": False, "error": "Internal Server Error"})

# -----------------------------
# 로컬 실행 진입점 (uvicorn)
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", 5000)), reload=True)

