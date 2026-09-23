"""Data models for Operations Service conforming to shared contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskModel(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = None
    site_zone: str
    target_volume_tons: float = Field(..., ge=0.0)
    completed_volume_tons: float = Field(default=0.0, ge=0.0)
    status: TaskStatus
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_duration_minutes: float = Field(..., ge=0.0)
    actual_duration_minutes: Optional[float] = Field(default=0.0, ge=0.0)
    assigned_operator_id: Optional[str] = None
    assigned_machine_id: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None


class TaskEstimateRequest(BaseModel):
    task_id: str
    operator_id: str
    machine_id: str
    remaining_volume_tons: float = Field(..., ge=0.0)
    weather_factor: float = Field(default=1.0, ge=0.5, le=2.0)
    terrain_grade_pct: float = Field(default=0.0)


class TaskTimeEstimateModel(BaseModel):
    task_id: str
    operator_id: str
    machine_id: str
    estimated_remaining_minutes: float = Field(..., ge=0.0)
    confidence_interval_p10_minutes: Optional[float] = None
    confidence_interval_p90_minutes: Optional[float] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    weather_impact_pct: Optional[float] = 0.0
    fatigue_impact_pct: Optional[float] = 0.0
    estimated_completion_time: datetime


class WhatIfRequestModel(BaseModel):
    task_id: str
    operator_id: str
    simulated_idle_reduction_pct: Optional[float] = Field(default=0.0, ge=0.0, le=100.0)
    weather_override: Optional[str] = None
    added_support_machines: Optional[int] = Field(default=0, ge=0)
    pace_multiplier: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)


class WhatIfResultModel(BaseModel):
    task_id: str
    baseline_eta_minutes: float
    simulated_eta_minutes: float
    time_saved_minutes: float
    fuel_saved_liters: float
    safety_risk_delta_pct: Optional[float] = 0.0
    summary: str


class SimilarShiftResultModel(BaseModel):
    shift_id: str
    similarity_score_pct: float = Field(..., ge=0.0, le=100.0)
    operator_tier: Optional[str] = "INTERMEDIATE"
    machine_model: Optional[str] = "CAT-349D"
    actual_duration_minutes: float
    total_volume_tons: float
    fuel_efficiency_tons_per_liter: Optional[float] = None
    safety_score: float
    key_takeaways: List[str] = Field(default_factory=list)


class ShiftContextModel(BaseModel):
    shift_id: str
    operator_id: str
    machine_id: str
    shift_start: datetime
    shift_status: str
    elapsed_minutes: float
    active_task_id: Optional[str] = None


class NextBestActionModel(BaseModel):
    action_id: str
    title: str
    rationale: str
    category: str
    priority: str
    estimated_benefit: Optional[str] = None


class ShiftTwinEnvironment(BaseModel):
    weather_condition: str
    ambient_temp_c: float
    ground_saturation_pct: float
    visibility_level: Optional[str] = "GOOD"


class ShiftTwinSafety(BaseModel):
    seatbelt_status: bool
    seatbelt_compliance_pct: float
    active_proximity_hazards: Optional[int] = 0
    safety_score: float


class ShiftTwinBehaviour(BaseModel):
    idle_percentage: float
    aggressive_events_count: Optional[int] = 0
    fatigue_risk_level: Optional[str] = "LOW"
    behaviour_score: float


class ShiftTwinProductivity(BaseModel):
    completed_volume_tons: float
    target_volume_tons: float
    pace_percentage: float
    efficiency_rating: Optional[str] = "HIGH"


class ShiftTwinPrediction(BaseModel):
    estimated_completion_time: datetime
    estimated_remaining_minutes: float
    delay_probability_pct: Optional[float] = 0.0
    confidence_score: float


class ShiftTwinModel(BaseModel):
    twin_id: str
    operator_id: str
    machine_id: str
    current_task_id: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    shift_health_score: float = Field(..., ge=0.0, le=100.0)
    environment: ShiftTwinEnvironment
    safety: ShiftTwinSafety
    behaviour: ShiftTwinBehaviour
    productivity: ShiftTwinProductivity
    prediction: ShiftTwinPrediction
    next_best_actions: List[NextBestActionModel] = Field(default_factory=list)
