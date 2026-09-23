"""SQLAlchemy ORM models for safety events, alerts, incidents, and behaviour."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
)
from .database import Base


class SafetyEventORM(Base):
    """Raw and processed telemetry event audit store."""

    __tablename__ = "safety_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    operator_id = Column(String(50), index=True, nullable=False)
    machine_id = Column(String(50), index=True, nullable=False)
    task_id = Column(String(50), nullable=True)
    speed_mps = Column(Float, default=0.0)
    seatbelt_status = Column(String(20), default="BUCKLED")
    proximity_distance_m = Column(Float, nullable=True)
    idle_minutes = Column(Float, nullable=True)
    machine_state = Column(String(30), nullable=True)
    raw_payload = Column(JSON, nullable=True)


class SafetyAlertORM(Base):
    """Safety alert log with acknowledged status and evidence."""

    __tablename__ = "safety_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    operator_id = Column(String(50), index=True, nullable=False)
    machine_id = Column(String(50), index=True, nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    acknowledged = Column(Boolean, default=False)
    distance_meters = Column(Float, nullable=True)
    evidence = Column(JSON, nullable=True)


class SafetyIncidentORM(Base):
    """Safety audit incident log with complete lifecycle (OPEN, ACKNOWLEDGED, RESOLVED)."""

    __tablename__ = "safety_incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    operator_id = Column(String(50), index=True, nullable=False)
    machine_id = Column(String(50), index=True, nullable=False)
    task_id = Column(String(50), nullable=True)
    incident_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    logged_by = Column(String(50), default="SYSTEM_AUTOMATED")
    status = Column(String(20), default="OPEN", index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(50), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(50), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)


class BehaviourMetricORM(Base):
    """Aggregated operator behavioral assessment and idle metrics."""

    __tablename__ = "behaviour_metrics"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(100), unique=True, index=True, nullable=False)
    operator_id = Column(String(50), index=True, nullable=False)
    machine_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    excessive_idling_score = Column(Float, default=0.0)
    aggressive_maneuver_count = Column(Integer, default=0)
    unsafe_speed_events = Column(Integer, default=0)
    cycle_consistency_pct = Column(Float, default=100.0)
    overall_behaviour_score = Column(Float, default=100.0)
    flags = Column(JSON, default=list)
    anomaly_detected = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)
    constraint_flags = Column(JSON, default=list)


class BehaviourAnomalyORM(Base):
    """Unusual machine or operator operational pattern event log."""

    __tablename__ = "behaviour_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(String(100), unique=True, index=True, nullable=False)
    operator_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    score = Column(Float, nullable=False)
    contributing_features = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
