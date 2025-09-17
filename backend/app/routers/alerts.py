from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import utcnow
from app.schemas.common import AlertCreate
from models.models import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("", status_code=201)
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
