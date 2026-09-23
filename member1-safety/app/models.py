"""Data models and schemas for Safety Service conforming to shared contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# ============================================================================
# Enums
# ============================================================================


class AlertSeverity(str, Enum):
    """Alert and incident severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProximityWarningLevel(str, Enum):
    """Proximity hazard warning tiers."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SafetyState(str, Enum):
    """Deterministic, unambiguous safety operational state."""

    SAFE = "SAFE"
    WARNING = "WARNING"
    HIGH_RISK = "HIGH_RISK"


class MachineState(str, Enum):
    """Discrete operational state of the heavy equipment."""

    STOPPED = "STOPPED"
    IDLE = "IDLE"
    WORKING = "WORKING"
    TRAMMING = "TRAMMING"
    ERROR = "ERROR"


class SeatbeltStatus(str, Enum):
    """Seatbelt physical sensor engagement state."""

    BUCKLED = "BUCKLED"
    UNBUCKLED = "UNBUCKLED"


class IncidentStatus(str, Enum):
    """Audit incident lifecycle state."""

    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class TrendDirection(str, Enum):
    """Direction of behavioral trend along a specific dimension."""

    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DEGRADING = "DEGRADING"


class ConstraintStatus(str, Enum):
    """Status of trajectory physical or operational constraint."""

    ACTIVE = "ACTIVE"
    CLEARED = "CLEARED"
    OVERRIDDEN = "OVERRIDDEN"


class SignalType(str, Enum):
    """Signal classification emitted for external consumers (e.g. Trajectory)."""

    SAFETY_INTERVENTION = "SAFETY_INTERVENTION"
    BEHAVIOUR_FLAG = "BEHAVIOUR_FLAG"
    TRAJECTORY_CONSTRAINT = "TRAJECTORY_CONSTRAINT"


class AlertType(str, Enum):
    """Safety alert types matching shared contracts and domain events."""

    SEATBELT_UNBUCKLED = "SEATBELT_UNBUCKLED"
    SEATBELT_VIOLATION = "SEATBELT_VIOLATION"
    PROXIMITY_HAZARD = "PROXIMITY_HAZARD"
    COMBINED_HAZARD = "COMBINED_HAZARD"
    EXCESSIVE_IDLE = "EXCESSIVE_IDLE"
    COLLISION_RISK = "COLLISION_RISK"
    SPEED_VIOLATION = "SPEED_VIOLATION"
    FATIGUE_WARNING = "FATIGUE_WARNING"
    ZONE_RESTRICTION = "ZONE_RESTRICTION"
    EQUIPMENT_OVERHEAT = "EQUIPMENT_OVERHEAT"
    UNSAFE_OPERATION = "UNSAFE_OPERATION"


class IncidentType(str, Enum):
    """Audit incident category classification."""

    COLLISION_NEAR_MISS = "COLLISION_NEAR_MISS"
    SEATBELT_VIOLATION = "SEATBELT_VIOLATION"
    ROLLOVER_RISK = "ROLLOVER_RISK"
    UNAUTHORIZED_ZONE_ENTRY = "UNAUTHORIZED_ZONE_ENTRY"
    EQUIPMENT_ABUSE = "EQUIPMENT_ABUSE"
    COMBINED_HAZARD = "COMBINED_HAZARD"
    PROXIMITY_BREACH = "PROXIMITY_BREACH"
    FATIGUE_CRITICAL = "FATIGUE_CRITICAL"


class ErrorCode(str, Enum):
    """Standardized error codes conforming to shared error.schema.json."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BAD_GATEWAY = "BAD_GATEWAY"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


# ============================================================================
# Telemetry Models (Nested + Dual-Format Support)
# ============================================================================


class GeoLocation(BaseModel):
    """Geographic coordinate representation."""

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation_m: Optional[float] = None


class MachineTelemetry(BaseModel):
    """Machine sensor telemetry."""

    engine_rpm: float = Field(..., ge=0)
    engine_temp_c: float
    hydraulic_pressure_kpa: float = Field(..., ge=0)
    fuel_rate_lph: float = Field(..., ge=0)
    speed_kmh: float = Field(..., ge=0)
    location: Optional[GeoLocation] = None
    operating_hours: Optional[float] = Field(default=0.0, ge=0)
    active_fault_codes: List[str] = Field(default_factory=list)


class OperatorTelemetry(BaseModel):
    """Operator sensor telemetry."""

    seatbelt_fastened: bool
    fatigue_score: float = Field(..., ge=0.0, le=100.0)
    heart_rate_bpm: Optional[int] = Field(default=None, ge=30, le=220)
    continuous_hours: Optional[float] = Field(default=0.0, ge=0.0)


class EnvironmentTelemetry(BaseModel):
    """Surrounding environmental telemetry."""

    weather_condition: str = "CLEAR"
    ambient_temp_c: float = 22.0
    ground_saturation_pct: float = Field(default=15.0, ge=0.0, le=100.0)
    terrain_grade_pct: Optional[float] = 0.0
    visibility_meters: Optional[float] = 1000.0


class TelemetryEventInput(BaseModel):
    """
    Ingested telemetry event.

    Supports both:
    1. Canonical nested format (machine, operator, environment).
    2. Flat sensor format (seatbelt_status, proximity_distance_m, machine_state,
       machine_speed_mps, idle_minutes, fuel_used_l, engine_hours).
    """

    event_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    machine_id: str
    operator_id: str
    task_id: Optional[str] = None

    # Canonical nested objects
    machine: MachineTelemetry
    operator: OperatorTelemetry
    environment: Optional[EnvironmentTelemetry] = None

    # Optional flat fields
    engine_hours: Optional[float] = None
    fuel_used_l: Optional[float] = None
    load_cycles: Optional[int] = None
    idle_minutes: Optional[float] = None
    seatbelt_status: Optional[str] = None
    proximity_distance_m: Optional[float] = None
    machine_state: Optional[str] = None
    machine_speed_mps: Optional[float] = None
    fuel_rate_lph: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_dual_formats(cls, data: Any) -> Any:
        """Harmonize flat sensor fields with nested telemetry contracts."""
        if not isinstance(data, dict):
            return data

        # If machine is missing or incomplete, build from flat fields
        machine_data = data.get("machine")
        if not isinstance(machine_data, dict):
            speed_mps = data.get("machine_speed_mps", 0.0)
            speed_kmh = float(speed_mps) * 3.6 if speed_mps is not None else 0.0
            fuel_rate = data.get("fuel_rate_lph", 15.0)
            engine_hours = data.get("engine_hours", 0.0)
            machine_data = {
                "engine_rpm": 1800.0 if speed_kmh > 0.5 else 800.0,
                "engine_temp_c": 85.0,
                "hydraulic_pressure_kpa": 22000.0,
                "fuel_rate_lph": fuel_rate if fuel_rate is not None else 15.0,
                "speed_kmh": speed_kmh,
                "operating_hours": engine_hours if engine_hours is not None else 0.0,
                "active_fault_codes": [],
            }
            data["machine"] = machine_data

        # If operator is missing or incomplete, build from flat fields
        op_data = data.get("operator")
        if not isinstance(op_data, dict):
            sb_status = data.get("seatbelt_status", "BUCKLED")
            seatbelt_fastened = (
                sb_status == "BUCKLED"
                if isinstance(sb_status, str)
                else bool(sb_status)
            )
            op_data = {
                "seatbelt_fastened": seatbelt_fastened,
                "fatigue_score": 20.0,
                "continuous_hours": 2.0,
            }
            data["operator"] = op_data

        # Ensure flat fields are synchronized if provided in nested format
        if "seatbelt_status" not in data or data["seatbelt_status"] is None:
            sb_fastened = data["operator"].get("seatbelt_fastened", True)
            data["seatbelt_status"] = "BUCKLED" if sb_fastened else "UNBUCKLED"

        if "machine_speed_mps" not in data or data["machine_speed_mps"] is None:
            sp_kmh = data["machine"].get("speed_kmh", 0.0)
            data["machine_speed_mps"] = round(float(sp_kmh) / 3.6, 3)

        if "fuel_rate_lph" not in data or data["fuel_rate_lph"] is None:
            data["fuel_rate_lph"] = data["machine"].get("fuel_rate_lph", 15.0)

        return data


# ============================================================================
# Alerts, Incidents, Constraints & Behaviour Signals
# ============================================================================


class ConstraintSignal(BaseModel):
    """
    Deterministic safety or operational constraint emitted for CAT Trajectory.
    Provides explainable evidence so Trajectory can prune infeasible actions.
    """

    signal_id: str
    operator_id: str
    machine_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    constraint_type: str  # e.g., "SPEED_LIMIT", "TASK_HOLD", "ROUTE_DEVIATION", "SUPERVISOR_INTERVENTION"
    status: ConstraintStatus = ConstraintStatus.ACTIVE
    severity: AlertSeverity = AlertSeverity.MEDIUM
    rationale: str
    recommended_action: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None


class BehaviourSignal(BaseModel):
    """Statistical deviation signal along a specific behavioral axis."""

    signal_id: str
    operator_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signal_type: SignalType = SignalType.BEHAVIOUR_FLAG
    feature_name: str
    observed_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    trend: TrendDirection = TrendDirection.STABLE
    description: str


class SafetyAlertModel(BaseModel):
    """Safety alert conforming to safety.schema.json."""

    alert_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operator_id: str
    machine_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    acknowledged: bool = False
    distance_meters: Optional[float] = None
    evidence: Optional[Dict[str, Any]] = None


class IncidentModel(BaseModel):
    """Audit incident log conforming to safety.schema.json with lifecycle management."""

    incident_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operator_id: str
    machine_id: str
    task_id: Optional[str] = None
    incident_type: str
    severity: AlertSeverity
    description: str
    logged_by: str = "SYSTEM_AUTOMATED"
    status: IncidentStatus = IncidentStatus.OPEN
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


class IncidentAcknowledgeRequest(BaseModel):
    """Request payload to acknowledge an incident."""

    acknowledged_by: str = "SUPERVISOR_CONSOLE"


class IncidentResolveRequest(BaseModel):
    """Request payload to resolve an incident."""

    resolved_by: str = "SUPERVISOR_CONSOLE"
    resolution_notes: str = Field(..., min_length=3)


class SafetyStatusModel(BaseModel):
    """
    Operator safety compliance status strictly conforming to safety.schema.json,
    with deterministic safety state and active constraint context.
    """

    operator_id: str
    machine_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    seatbelt_fastened: bool
    seatbelt_compliance_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    proximity_warning_level: ProximityWarningLevel = ProximityWarningLevel.NONE
    active_hazard_count: int = Field(default=0, ge=0)
    overall_safety_score: float = Field(default=100.0, ge=0.0, le=100.0)

    # Architectural extensions
    safety_state: SafetyState = SafetyState.SAFE
    active_alerts: List[SafetyAlertModel] = Field(default_factory=list)
    active_constraints: List[ConstraintSignal] = Field(default_factory=list)


class BehaviourAnalysisModel(BaseModel):
    """
    Operator behavior rating and idle metrics conforming to behaviour.schema.json.
    Includes deterministic constraint flags for CAT Trajectory.
    """

    analysis_id: Optional[str] = None
    operator_id: str
    machine_id: str = "EXC-CAT-001"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    excessive_idling_score: float = Field(default=10.0, ge=0.0, le=100.0)
    aggressive_maneuver_count: int = Field(default=0, ge=0)
    unsafe_speed_events: int = Field(default=0, ge=0)
    cycle_consistency_pct: float = Field(default=92.0, ge=0.0, le=100.0)
    overall_behaviour_score: float = Field(default=95.0, ge=0.0, le=100.0)
    flags: List[str] = Field(default_factory=list)
    anomaly_detected: bool = False
    constraint_flags: Optional[List[str]] = Field(default_factory=list)

    # Optional granular behavioral diagnostics (separate axes - not a single composite)
    anomaly_score: Optional[float] = None
    trends: Optional[Dict[str, TrendDirection]] = None
    signals: Optional[List[BehaviourSignal]] = None


class ErrorResponseModel(BaseModel):
    """Standardized error response conforming to shared error.schema.json."""

    error_code: ErrorCode
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
