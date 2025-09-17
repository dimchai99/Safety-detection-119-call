import uuid as uuidlib
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import utcnow
from app.schemas.common import DeviceCreate
from models.models import Device

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("", status_code=201)
def register_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    if payload.serial:
        exists = db.query(Device).filter_by(serial=payload.serial).first()
        if exists:
            raise HTTPException(status_code=409, detail="serial_already_exists")

    d = Device(
        id=uuidlib.uuid4(),
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

@router.get("")
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

    return [{
        "id": str(d.id),
        "owner_id": str(d.owner_id) if d.owner_id else None,
        "name": d.name,
        "type": d.type,
        "serial": d.serial,
        "location": d.location,
        "is_active": d.is_active,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    } for d in q]

@router.get("/{device_id}")
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
