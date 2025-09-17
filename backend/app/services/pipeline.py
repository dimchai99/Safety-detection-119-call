from typing import Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from app.core.utils import utcnow
from models.models import Event, Incident, Alert

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
        existing = db.query(Event).filter_by(idx_idempotency=idx_idem).first()
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
