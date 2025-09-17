import hashlib
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.core.config import DEVICE_SHARED_SECRET
from app.core.security import verify_signature
from app.core.utils import utcnow
from app.schemas.common import EventIngest
from app.services.pipeline import (
    run_detection, save_event, open_or_update_incident, enqueue_alerts
)
from models.models import Device

router = APIRouter(tags=["ingest"])

@router.post("/ingest", status_code=201)
async def ingest(
    request: Request,
    body: EventIngest,
    x_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    raw = await request.body()
    if not verify_signature(raw, x_signature, DEVICE_SHARED_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    exists = db.execute(
        select(Device.id).where(Device.id == str(body.device_id))
    ).scalar_one_or_none()
    if not exists:
        raise HTTPException(status_code=400, detail="unknown device_id")

    occurred_iso = (body.occurred_at or utcnow()).isoformat()
    idem = body.idx_idempotency or hashlib.sha1(
        f"{body.device_id}:{occurred_iso}:{body.event_type}".encode()
    ).hexdigest()

    bdict = body.model_dump()
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
