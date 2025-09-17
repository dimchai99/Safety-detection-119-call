# models.py
from datetime import datetime
from sqlalchemy import (
    Text, Boolean, Integer, BigInteger, Numeric, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="user")
    nickname: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # relationships
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="owner")
    confirmations: Mapped[list["Confirmation"]] = relationship("Confirmation", back_populates="actor")

class Device(Base):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    owner_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    name: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str | None] = mapped_column(Text)
    serial: Mapped[str | None] = mapped_column(Text, unique=True)
    location: Mapped[dict | None] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # relationships
    owner: Mapped["User"] = relationship("User", back_populates="devices")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="device")
    incidents: Mapped[list["Incident"]] = relationship("Incident", back_populates="device")

class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    device_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="open")
    category: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(Text)
    top_signals: Mapped[dict | None] = mapped_column(JSONB)
    opened_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # relationships
    device: Mapped["Device"] = relationship("Device", back_populates="incidents")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="incident")
    confirmations: Mapped[list["Confirmation"]] = relationship("Confirmation", back_populates="incident")
    escalations: Mapped[list["Escalation"]] = relationship("Escalation", back_populates="incident")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    device_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"))
    event_type: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    risk_score: Mapped[Numeric | None] = mapped_column(Numeric)
    risk_level: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    idx_idempotency: Mapped[str | None] = mapped_column(Text, unique=True)

    # relationships
    device: Mapped["Device"] = relationship("Device", back_populates="events")

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    incident_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    channel: Mapped[str | None] = mapped_column(Text)
    target: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="alerts")

class Confirmation(Base):
    __tablename__ = "confirmations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    incident_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    actor_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    decision: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="confirmations")
    actor: Mapped["User"] = relationship("User", back_populates="confirmations")

class Escalation(Base):
    __tablename__ = "escalations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    incident_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    step: Mapped[int | None] = mapped_column(Integer)
    action: Mapped[str | None] = mapped_column(Text)
    executed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    result: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSONB)

    # relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="escalations")

class Rule(Base):
    __tablename__ = "rules"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    definition: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    actor: Mapped[str | None] = mapped_column(Text)
    action: Mapped[str | None] = mapped_column(Text)
    entity: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
