from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import utcnow
from app.schemas.common import EventIngest
from models.models import Event

router = APIRouter(prefix="/events", tags=["events"])

@router.post("", status_code=201)
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
