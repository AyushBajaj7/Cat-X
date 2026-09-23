"""
Shift Twin Digital Context Builder.
Constructs canonical 7-dimension Shift Twin representation fusing machine, operator,
task, environment, safety, behaviour, and productivity with CAT Trajectory state.
Conforms strictly to shared/contracts/shift-twin.schema.json.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from ..models import (
    NextBestActionModel,
    ShiftTwinBehaviour,
    ShiftTwinEnvironment,
    ShiftTwinModel,
    ShiftTwinPrediction,
    ShiftTwinProductivity,
    ShiftTwinSafety,
)
from .operational_state import OperationalState


def build_shift_twin(
    state: OperationalState,
    attention_mode: str = "NORMAL",
    next_best_actions: Optional[List[NextBestActionModel]] = None,
    decision_point: Optional[Dict[str, Any]] = None,
    trajectory_options: Optional[List[Dict[str, Any]]] = None,
    decision_trace: Optional[List[Dict[str, Any]]] = None,
    similar_contexts: Optional[List[Dict[str, Any]]] = None,
    latest_decision_memory: Optional[Dict[str, Any]] = None,
) -> ShiftTwinModel:
    """Builds canonical ShiftTwinModel from live OperationalState and Trajectory engine state."""
    now = datetime.now(timezone.utc)

    # 1. Environment
    env = ShiftTwinEnvironment(
        weather_condition=state.environment.weather_condition,
        ambient_temp_c=state.environment.ambient_temp_c,
        ground_saturation_pct=state.environment.ground_saturation_pct,
        visibility_level=state.environment.visibility_level,
    )

    # 2. Safety (from Engineer 1 signals)
    safety = ShiftTwinSafety(
        seatbelt_status=state.safety_signals.seatbelt_status,
        seatbelt_compliance_pct=state.safety_signals.seatbelt_compliance_pct,
        active_proximity_hazards=state.safety_signals.active_proximity_hazards,
        safety_score=state.safety_signals.safety_score,
    )

    # 3. Behaviour (from Engineer 1 signals)
    fatigue = "LOW"
    if state.task_progress.elapsed_minutes > 300:
        fatigue = "HIGH"
    elif state.task_progress.elapsed_minutes > 180:
        fatigue = "MODERATE"

    behaviour = ShiftTwinBehaviour(
        idle_percentage=state.idle_state.idle_percentage,
        aggressive_events_count=state.behaviour_signals.aggressive_maneuver_count,
        fatigue_risk_level=fatigue,
        behaviour_score=state.behaviour_signals.overall_behaviour_score,
    )

    # 4. Productivity
    prod = ShiftTwinProductivity(
        completed_volume_tons=state.current_task.completed_volume_tons,
        target_volume_tons=state.current_task.target_volume_tons,
        pace_percentage=state.task_progress.pace_ratio * 100.0,
        efficiency_rating=state.productivity_state.efficiency_rating,
    )

    # 5. Prediction
    pred = ShiftTwinPrediction(
        estimated_completion_time=state.prediction_state.estimated_completion_time,
        estimated_remaining_minutes=state.prediction_state.estimated_remaining_minutes,
        delay_probability_pct=state.prediction_state.delay_probability_pct,
        confidence_score=state.prediction_state.confidence_score,
    )

    # Calculate composite shift health score (0-100)
    # Weighted composite: 40% Safety, 25% Behaviour, 20% Productivity, 15% Schedule alignment
    schedule_health = max(0.0, 100.0 - (state.prediction_state.delay_probability_pct * 1.5))
    composite_health = (
        (safety.safety_score * 0.40) +
        (behaviour.behaviour_score * 0.25) +
        (min(100.0, prod.pace_percentage) * 0.20) +
        (schedule_health * 0.15)
    )
    shift_health_score = float(round(composite_health, 1))

    # Shift forecast
    scheduled_minutes = state.current_task.estimated_duration_minutes
    projected_minutes = state.task_progress.elapsed_minutes + state.prediction_state.estimated_remaining_minutes
    shift_delay_minutes = max(0.0, projected_minutes - scheduled_minutes)

    shift_forecast = {
        "scheduled_completion_minutes": scheduled_minutes,
        "projected_completion_minutes": round(projected_minutes, 1),
        "difference_minutes": round(shift_delay_minutes, 1),
        "weather_risk_level": "ELEVATED" if state.environment.weather_condition in ["RAIN", "MUD"] else "NOMINAL",
        "projected_shift_fuel_litres": round(
            state.idle_state.idle_fuel_wasted_litres + (projected_minutes / 60.0) * 32.0, 1
        ),
    }

    actions = next_best_actions or [
        NextBestActionModel(
            action_id="NBA-01",
            title="Maintain Digging Envelope",
            rationale="Current cycle cadence is aligned with shift targets.",
            category="EFFICIENCY",
            priority="NORMAL",
            estimated_benefit="Keeps current schedule on track.",
        )
    ]

    twin = ShiftTwinModel(
        twin_id=f"TWIN-{state.operator.operator_id}-LIVE",
        operator_id=state.operator.operator_id,
        machine_id=state.machine.machine_id,
        current_task_id=state.current_task.task_id,
        updated_at=now,
        shift_health_score=shift_health_score,
        environment=env,
        safety=safety,
        behaviour=behaviour,
        productivity=prod,
        prediction=pred,
        next_best_actions=actions,
    )

    # Convert to schema dict if needed or return model with extras
    return twin
