"""Data models for Safety Service conforming to shared contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProximityWarningLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GeoLocation(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation_m: Optional[float] = None


class MachineTelemetry(BaseModel):
    engine_rpm: float = Field(..., ge=0)
    engine_temp_c: float
    hydraulic_pressure_kpa: float = Field(..., ge=0)
    fuel_rate_lph: float = Field(..., ge=0)
    speed_kmh: float = Field(..., ge=0)
    location: Optional[GeoLocation] = None
    operating_hours: Optional[float] = Field(default=0.0, ge=0)
    active_fault_codes: List[str] = Field(default_factory=list)


class OperatorTelemetry(BaseModel):
    seatbelt_fastened: bool
    fatigue_score: float = Field(..., ge=0.0, le=100.0)
    heart_rate_bpm: Optional[int] = Field(default=None, ge=30, le=220)
    continuous_hours: Optional[float] = Field(default=0.0, ge=0.0)


class EnvironmentTelemetry(BaseModel):
    weather_condition: str = "CLEAR"
    ambient_temp_c: float = 22.0
    ground_saturation_pct: float = Field(default=15.0, ge=0.0, le=100.0)
    terrain_grade_pct: Optional[float] = 0.0
    visibility_meters: Optional[float] = 1000.0


class TelemetryEventInput(BaseModel):
    event_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    machine_id: str
    operator_id: str
    task_id: Optional[str] = None
    machine: MachineTelemetry
    operator: OperatorTelemetry
    environment: Optional[EnvironmentTelemetry] = None


class SafetyAlertModel(BaseModel):
    alert_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operator_id: str
    machine_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    acknowledged: bool = False
    distance_meters: Optional[float] = None


class IncidentModel(BaseModel):
    incident_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operator_id: str
    machine_id: str
    task_id: Optional[str] = None
    incident_type: str
    severity: AlertSeverity
    description: str
    logged_by: str


class BehaviourAnalysisModel(BaseModel):
    analysis_id: str
    operator_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    excessive_idling_score: float = Field(default=12.0, ge=0.0, le=100.0)
    aggressive_maneuver_count: int = Field(default=0, ge=0)
    unsafe_speed_events: int = Field(default=0, ge=0)
    cycle_consistency_pct: float = Field(default=92.5, ge=0.0, le=100.0)
    overall_behaviour_score: float = Field(default=94.0, ge=0.0, le=100.0)
    flags: List[str] = Field(default_factory=list)


class SafetyStatusModel(BaseModel):
    operator_id: str
    machine_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    seatbelt_fastened: bool
    seatbelt_compliance_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    proximity_warning_level: ProximityWarningLevel = ProximityWarningLevel.NONE
    active_hazard_count: int = Field(default=0, ge=0)
    overall_safety_score: float = Field(default=98.0, ge=0.0, le=100.0)


class ErrorResponseModel(BaseModel):
    error_code: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[Dict[str, Any]] = None
