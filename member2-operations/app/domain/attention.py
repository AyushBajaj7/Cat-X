"""
CAT Trajectory — Adaptive Attention Mode Engine.
Dynamically sets the Operator Cockpit focus mode using transparent, deterministic rules.
Valid Focus Modes:
- SAFETY_FOCUS: Critical safety proximity or seatbelt condition active
- DECISION_FOCUS: Tactical decision point detected by Trajectory engine
- PLANNING_FOCUS: Shift delay risk pushing completion past handoff
- EFFICIENCY_FOCUS: Unproductive high/low idle exceeding baseline
- TRAINING_FOCUS: Specific operator technique certification/gap flagged
- NORMAL: Nominal operations on schedule
"""

from typing import Tuple
from .operational_state import OperationalState


def resolve_attention_mode(
    state: OperationalState,
    has_active_decision_point: bool = False
) -> Tuple[str, str]:
    """
    Evaluates operational state and returns (attention_mode, attention_reason)
    following strict priority hierarchy.
    """
    # 1. Highest Priority: Critical Safety
    if (
        not state.safety_signals.seatbelt_status
        or state.safety_signals.active_proximity_hazards > 0
        or state.environment.slope_deg >= 14.0
    ):
        return (
            "SAFETY_FOCUS",
            "Safety perimeter threshold approached: immediate operator attention required."
        )

    # 2. Second Priority: Active Tactical Decision Point
    if has_active_decision_point:
        return (
            "DECISION_FOCUS",
            "CAT Trajectory detected operational inflection point: candidate trajectories ready for review."
        )

    # 3. Third Priority: Schedule / Shift Delay Risk
    scheduled = state.current_task.estimated_duration_minutes
    projected = state.task_progress.elapsed_minutes + state.prediction_state.estimated_remaining_minutes
    if (projected - scheduled) >= 10.0 or state.prediction_state.delay_probability_pct >= 25.0:
        return (
            "PLANNING_FOCUS",
            f"Projected completion delayed by {round(projected - scheduled, 1)} min past shift target."
        )

    # 4. Fourth Priority: Efficiency / Idle Deviation
    if state.idle_state.idle_percentage >= 15.0 or state.idle_state.high_idle_flag:
        return (
            "EFFICIENCY_FOCUS",
            f"Low idle reached {state.idle_state.idle_percentage:.1f}%, exceeding 15% efficiency benchmark."
        )

    # 5. Fifth Priority: Skill / Training Gap
    if (
        state.operator.experience_tier == "NOVICE"
        and state.productivity_state.cycle_time_sec > 34.0
    ):
        return (
            "TRAINING_FOCUS",
            "Cycle consistency variance suggests micro-module review on trench grading technique."
        )

    # Default: Nominal Operation
    return (
        "NORMAL",
        "Operations proceeding within nominal tolerances. Target cadence maintained."
    )
