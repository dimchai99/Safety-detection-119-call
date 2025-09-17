import uuid as uuidlib
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import utcnow
from app.schemas.common import IncidentCreate, IncidentStatusUpdate
from models.models import Incident

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.post("", status_code=201)
def open_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    inc = Incident(
        id=uuidlib.uuid4(),
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

@router.post("/{incident_id}/status")
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

@router.get("/by-device/{device_id}")
def list_incidents_by_device(device_id: UUID, db: Session = Depends(get_db)):
    q = (
        db.query(Incident)
        .filter(Incident.device_id == str(device_id))
        .order_by(Incident.opened_at.desc())
        .limit(50)
    )
    return [{
        "id": str(x.id),
        "status": x.status,
        "category": x.category,
        "risk_level": x.risk_level,
        "opened_at": x.opened_at.isoformat() if x.opened_at else None,
    } for x in q]
