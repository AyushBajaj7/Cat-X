"""
SQLAlchemy ORM Models for Operations Service.
Owns exclusively the operations domain tables in operations_schema:
- operations_tasks
- operations_predictions
- shift_contexts
- shift_forecasts
- decision_points
- trajectory_scenarios
- trajectory_outcomes
- decision_memory
- similar_contexts

Strict Rule: Does NOT define or access safety_schema or training_schema tables.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OperationsTask(Base):
    __tablename__ = "operations_tasks"

    task_id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    site_zone = Column(String(64), nullable=False)
    target_volume_tons = Column(Float, nullable=False, default=0.0)
    completed_volume_tons = Column(Float, nullable=False, default=0.0)
    status = Column(String(32), nullable=False, default="PENDING")
    priority = Column(String(32), nullable=False, default="NORMAL")
    estimated_duration_minutes = Column(Float, nullable=False, default=0.0)
    actual_duration_minutes = Column(Float, nullable=True, default=0.0)
    assigned_operator_id = Column(String(64), nullable=True)
    assigned_machine_id = Column(String(64), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)


class OperationsPrediction(Base):
    __tablename__ = "operations_predictions"

    prediction_id = Column(String(64), primary_key=True)
    task_id = Column(String(64), nullable=False)
    operator_id = Column(String(64), nullable=False)
    machine_id = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    estimated_remaining_minutes = Column(Float, nullable=False)
    confidence_interval_p10_minutes = Column(Float, nullable=True)
    confidence_interval_p90_minutes = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=False)
    weather_impact_pct = Column(Float, default=0.0)
    fatigue_impact_pct = Column(Float, default=0.0)


class ShiftContextRecord(Base):
    __tablename__ = "shift_contexts"

    shift_id = Column(String(64), primary_key=True)
    operator_id = Column(String(64), nullable=False)
    machine_id = Column(String(64), nullable=False)
    shift_start = Column(DateTime(timezone=True), nullable=False)
    shift_status = Column(String(32), nullable=False, default="ACTIVE")
    elapsed_minutes = Column(Float, nullable=False, default=0.0)
    active_task_id = Column(String(64), nullable=True)


class ShiftForecastRecord(Base):
    __tablename__ = "shift_forecasts"

    forecast_id = Column(String(64), primary_key=True)
    operator_id = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    projected_completion_minutes = Column(Float, nullable=False)
    scheduled_completion_minutes = Column(Float, nullable=False)
    delay_minutes = Column(Float, nullable=False)
    weather_risk_level = Column(String(32), default="NOMINAL")
    projected_fuel_litres = Column(Float, default=0.0)


class DecisionPointRecord(Base):
    __tablename__ = "decision_points"

    decision_point_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    operator_id = Column(String(64), nullable=False)
    machine_id = Column(String(64), nullable=False)
    task_id = Column(String(64), nullable=False)
    trigger_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    summary = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False, default="{}")
    available_actions_json = Column(Text, nullable=False, default="[]")


class TrajectoryScenarioRecord(Base):
    __tablename__ = "trajectory_scenarios"

    scenario_id = Column(String(64), primary_key=True)
    decision_point_id = Column(String(64), nullable=False)
    action_id = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    parameters_json = Column(Text, nullable=False, default="{}")
    constraint_status = Column(String(32), nullable=False)
    predicted_outcome_json = Column(Text, nullable=False, default="{}")
    explanation = Column(Text, nullable=False)


class TrajectoryOutcomeRecord(Base):
    __tablename__ = "trajectory_outcomes"

    outcome_id = Column(String(64), primary_key=True)
    decision_id = Column(String(64), nullable=False)
    actual_duration_minutes = Column(Float, nullable=False)
    actual_fuel_litres = Column(Float, nullable=True)
    actual_idle_minutes = Column(Float, nullable=True)
    prediction_error_json = Column(Text, nullable=False, default="{}")
    drift_status = Column(String(32), default="WITHIN_TOLERANCE")
    is_simulation = Column(Boolean, default=False)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DecisionMemoryRecord(Base):
    __tablename__ = "decision_memory"

    decision_id = Column(String(64), primary_key=True)
    operator_id = Column(String(64), nullable=False)
    machine_id = Column(String(64), nullable=False)
    task_id = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    context_signature = Column(String(128), nullable=False)
    available_scenarios_json = Column(Text, nullable=False, default="[]")
    chosen_scenario = Column(String(64), nullable=False)
    predicted_outcome_json = Column(Text, nullable=False, default="{}")
    actual_outcome_json = Column(Text, nullable=True)
    prediction_error_json = Column(Text, nullable=True)
    operator_reason = Column(Text, nullable=False)
    source = Column(String(64), nullable=False, default="OPERATOR_MANUAL_SELECT")


class SimilarContextRecord(Base):
    __tablename__ = "similar_contexts"

    context_id = Column(String(64), primary_key=True)
    shift_id = Column(String(64), nullable=False)
    context_signature = Column(String(128), nullable=False)
    similarity_score_pct = Column(Float, nullable=False)
    chosen_action = Column(String(64), nullable=True)
    actual_time_saved_minutes = Column(Float, nullable=True)
    actual_fuel_saved_liters = Column(Float, nullable=True)
    key_learning = Column(Text, nullable=True)
