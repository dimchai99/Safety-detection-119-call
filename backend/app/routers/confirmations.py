from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import utcnow
from app.schemas.common import ConfirmationCreate
from models.models import Confirmation

router = APIRouter(prefix="/confirmations", tags=["confirmations"])

@router.post("", status_code=201)
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
