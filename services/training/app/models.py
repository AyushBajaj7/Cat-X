"""Data models for Training Service conforming to shared contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TrainingCategory(str, Enum):
    SAFETY = "SAFETY"
    ECO_OPERATION = "ECO_OPERATION"
    MACHINE_HANDLING = "MACHINE_HANDLING"
    SITE_PROCEDURES = "SITE_PROCEDURES"


class TrainingDifficulty(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class TrainingUrgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TrainingModuleModel(BaseModel):
    module_id: str
    title: str
    category: TrainingCategory
    target_machine_category: str = "EXCAVATOR"
    estimated_duration_minutes: int = Field(..., ge=1)
    difficulty: TrainingDifficulty
    description: str
    learning_objectives: List[str] = Field(default_factory=list)
    simulator_scenario_id: Optional[str] = None


class TrainingRecommendationModel(BaseModel):
    recommendation_id: str
    operator_id: str
    module_id: str
    module_title: str
    urgency: TrainingUrgency
    trigger_source: str
    reason: str
    recommended_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrainingAttemptInput(BaseModel):
    operator_id: str
    module_id: str
    score_pct: float = Field(..., ge=0.0, le=100.0)
    time_spent_seconds: int = Field(..., ge=0)
    feedback: Optional[str] = None


class TrainingAttemptModel(BaseModel):
    attempt_id: str
    operator_id: str
    module_id: str
    score_pct: float = Field(..., ge=0.0, le=100.0)
    passed: bool
    time_spent_seconds: int = Field(..., ge=0)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    feedback: Optional[str] = None


class TrainingProgressModel(BaseModel):
    operator_id: str
    completed_modules_count: int = Field(default=0, ge=0)
    average_score_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    certifications_earned: List[str] = Field(default_factory=list)
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
