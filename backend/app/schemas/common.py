from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: str
    role: Optional[str] = "user"
    nickname: Optional[str] = None
    phone: Optional[str] = None

class DeviceCreate(BaseModel):
    owner_id: Optional[UUID] = None
    name: Optional[str] = None
    type: Optional[str] = None
    serial: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

class EventIngest(BaseModel):
    device_id: UUID
    event_type: str
    occurred_at: Optional[datetime] = None
    payload: Optional[Dict[str, Any]] = None
    idx_idempotency: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None

class IncidentCreate(BaseModel):
    device_id: UUID
    category: Optional[str] = None
    risk_level: Optional[str] = None
    top_signals: Optional[Dict[str, Any]] = None

class IncidentStatusUpdate(BaseModel):
    status: str  # "open" | "acknowledged" | "closed"

class AlertCreate(BaseModel):
    incident_id: UUID
    channel: Optional[str] = None
    target: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    status: Optional[str] = "queued"
    error: Optional[str] = None

class ConfirmationCreate(BaseModel):
    incident_id: UUID
    actor_id: UUID
    decision: Optional[str] = None
    reason: Optional[str] = None
