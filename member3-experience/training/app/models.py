"""Data models for Training Service conforming to shared contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


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


class ScenarioChoice(BaseModel):
    choice_id: str
    text: str
    is_correct: bool
    explanation: str


class ScenarioStep(BaseModel):
    step_number: int
    title: str
    prompt: str
    choices: List[ScenarioChoice] = Field(default_factory=list)


class TrainingModuleModel(BaseModel):
    module_id: str
    title: str
    description: str
    objective: str
    difficulty: str
    estimated_minutes: int = Field(..., ge=1)
    skills: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    scenario_steps: List[ScenarioStep] = Field(default_factory=list)
    category: TrainingCategory = TrainingCategory.SAFETY
    target_machine_category: str = "EXCAVATOR"
    estimated_duration_minutes: Optional[int] = None
    learning_objectives: List[str] = Field(default_factory=list)
    simulator_scenario_id: Optional[str] = None

    @model_validator(mode="after")
    def sync_contract_fields(self):
        if self.estimated_duration_minutes is None:
            self.estimated_duration_minutes = self.estimated_minutes
        if not self.learning_objectives and self.steps:
            self.learning_objectives = list(self.steps)
        return self


class TrainingRecommendationModel(BaseModel):
    recommendation_id: str
    operator_id: str
    module_id: str
    module_title: str
    urgency: TrainingUrgency
    trigger_source: str
    reason: str
    recommended_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signal: Optional[str] = None
    value: Optional[str] = None


class TrainingAttemptInput(BaseModel):
    operator_id: str
    module_id: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    mistakes: int = Field(default=0, ge=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "COMPLETED"
    score_pct: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    feedback: Optional[str] = None

    @model_validator(mode="after")
    def normalize_compatibility(self):
        if self.score is None:
            self.score = self.score_pct
        if self.max_score is None:
            self.max_score = 100.0 if self.score is not None else 100.0
        if self.score is None:
            self.score = 0.0
        if self.max_score is None or self.max_score <= 0:
            self.max_score = 100.0
        if self.time_spent_seconds is None:
            self.time_spent_seconds = 0
        return self


class TrainingAttemptModel(BaseModel):
    attempt_id: str
    operator_id: str
    module_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    score: float = Field(..., ge=0.0)
    max_score: float = Field(..., gt=0.0)
    percentage: float = Field(..., ge=0.0, le=100.0)
    mistakes: int = Field(default=0, ge=0)
    passed: bool
    status: str = "COMPLETED"
    score_pct: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    feedback: Optional[str] = None

    @model_validator(mode="after")
    def sync_attempt_fields(self):
        if self.score_pct is None:
            self.score_pct = self.percentage
        if self.time_spent_seconds is None:
            self.time_spent_seconds = int((self.completed_at - self.started_at).total_seconds()) if self.completed_at and self.started_at else 0
        return self


class TrainingProgressModel(BaseModel):
    operator_id: str
    completed_modules_count: int = Field(default=0, ge=0)
    average_score_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    certifications_earned: List[str] = Field(default_factory=list)
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
