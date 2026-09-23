"""
Canonical Operational State Model (Owned by Engineer 2).
Serves as the unified 13-dimension live operational snapshot and primary input
to the CAT Trajectory Consequence Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OperatorInfo(BaseModel):
    operator_id: str
    name: str
    experience_tier: str = "INTERMEDIATE"  # NOVICE, INTERMEDIATE, EXPERT, MASTER
    total_operating_hours: float = 1420.0


class MachineInfo(BaseModel):
    machine_id: str
    model: str = "CAT-349D"
    category: str = "EXCAVATOR"
    payload_capacity_tons: float = 28.0
    status: str = "OPERATIONAL"
    total_operating_hours: float = 3450.0
    machine_age_years: float = 3.5


class TaskInfo(BaseModel):
    task_id: str
    title: str
    site_zone: str
    target_volume_tons: float
    completed_volume_tons: float = 0.0
    status: str = "IN_PROGRESS"
    priority: str = "CRITICAL"
    estimated_duration_minutes: float = 240.0


class TaskProgress(BaseModel):
    pct_complete: float
    volume_remaining_tons: float
    elapsed_minutes: float
    pace_ratio: float = 1.0


class EnvironmentState(BaseModel):
    weather_condition: str = "CLEAR"
    ambient_temp_c: float = 24.0
    ground_saturation_pct: float = 14.0
    visibility_level: str = "GOOD"
    slope_deg: float = 4.0


class QueueState(BaseModel):
    queue_length: int = 1
    truck_arrival_interval_min: float = 6.0
    trucks_in_transit: int = 4
    bottleneck_severity: str = "LOW"  # LOW, MODERATE, SEVERE


class MachineState(BaseModel):
    engine_rpm: float = 1800.0
    engine_load_pct: float = 72.0
    hydraulic_pressure_bar: float = 310.0
    swing_angle_deg: float = 48.0
    fuel_rate_lph: float = 34.5


class IdleState(BaseModel):
    idle_minutes: float = 14.0
    idle_percentage: float = 12.0
    high_idle_flag: bool = False
    idle_fuel_wasted_litres: float = 3.2


class ProductivityState(BaseModel):
    tons_per_hour: float = 110.0
    cycle_time_sec: float = 28.0
    bucket_fill_factor: float = 0.92
    efficiency_rating: str = "HIGH"


class SafetySignals(BaseModel):
    seatbelt_status: bool = True
    seatbelt_compliance_pct: float = 99.0
    active_proximity_hazards: int = 0
    safety_score: float = 98.0
    constraint_flags: List[str] = Field(default_factory=list)


class BehaviourSignals(BaseModel):
    excessive_idling_score: float = 12.0
    aggressive_maneuver_count: int = 0
    cycle_consistency_pct: float = 92.0
    overall_behaviour_score: float = 94.0
    anomaly_detected: bool = False
    flags: List[str] = Field(default_factory=list)


class PredictionState(BaseModel):
    estimated_remaining_minutes: float = 145.0
    estimated_completion_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delay_probability_pct: float = 5.0
    confidence_score: float = 0.90
    lower_minutes: Optional[float] = None
    upper_minutes: Optional[float] = None


class OperationalState(BaseModel):
    """Unified Canonical Operational State consumed by Trajectory and Twin engines."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operator: OperatorInfo
    machine: MachineInfo
    current_task: TaskInfo
    task_progress: TaskProgress
    environment: EnvironmentState
    queue_state: QueueState
    machine_state: MachineState
    idle_state: IdleState
    productivity_state: ProductivityState
    safety_signals: SafetySignals
    behaviour_signals: BehaviourSignals
    prediction_state: PredictionState
