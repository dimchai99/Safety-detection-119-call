import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import utcnow
from app.schemas.common import UserCreate
from models.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", status_code=201)
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
