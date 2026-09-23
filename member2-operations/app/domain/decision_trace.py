"""
CAT Trajectory — Decision Trace Engine.
Builds transparent, step-by-step explanatory traces connecting raw telemetry signals
and model inferences to operational recommendations and chosen scenarios.
"""

from typing import Any, Dict, List, Optional
from .operational_state import OperationalState


def build_decision_trace(
    state: OperationalState,
    decision_point: Optional[Dict[str, Any]] = None,
    chosen_scenario_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Generates an explainable signal-to-outcome decision trace."""
    trace_steps: List[Dict[str, Any]] = []

    # Step 1: Telemetry Signal Observation
    queue_len = state.queue_state.queue_length
    trace_steps.append({
        "step": 1,
        "phase": "OBSERVE_SIGNAL",
        "signal": "queue_length",
        "observed_value": queue_len,
        "baseline_value": 1,
        "interpretation": f"Truck queue reached {queue_len} units, indicating downstream crusher bottleneck.",
    })

    # Step 2: Truck Arrival Interval
    arrival_interval = state.queue_state.truck_arrival_interval_min
    trace_steps.append({
        "step": 2,
        "phase": "OBSERVE_SIGNAL",
        "signal": "truck_arrival_interval_min",
        "observed_value": arrival_interval,
        "baseline_value": 5.0,
        "interpretation": f"Platoon gap of {arrival_interval:.1f} minutes projected before next truck arrival.",
    })

    # Step 3: Compounding Idle Inference
    idle_pct = state.idle_state.idle_percentage
    trace_steps.append({
        "step": 3,
        "phase": "MODEL_INFERENCE",
        "signal": "idle_percentage",
        "observed_value": idle_pct,
        "baseline_value": 8.0,
        "interpretation": f"Low idle projected to accumulate to {idle_pct:.1f}% while excavator awaits platoon.",
    })

    # Step 4: Weather & Traction Degradation
    saturation = state.environment.ground_saturation_pct
    trace_steps.append({
        "step": 4,
        "phase": "ENVIRONMENT_INFERENCE",
        "signal": "ground_saturation_pct",
        "observed_value": saturation,
        "baseline_value": 12.0,
        "interpretation": f"Incoming rain front elevates saturation to {saturation:.1f}%, adding 3.5 min/trip to haul ramp.",
    })

    # Step 5: Shift Schedule Impact
    scheduled = state.current_task.estimated_duration_minutes
    projected = state.task_progress.elapsed_minutes + state.prediction_state.estimated_remaining_minutes
    delay = max(0.0, projected - scheduled)
    trace_steps.append({
        "step": 5,
        "phase": "CONSEQUENCE_FORECAST",
        "signal": "projected_shift_delay_minutes",
        "observed_value": round(delay, 1),
        "baseline_value": 0.0,
        "interpretation": f"Compounding effects result in an unrecoverable {delay:.1f}-minute shift handoff delay trap.",
    })

    # Step 6: Selected Tactical Mitigation
    if chosen_scenario_id:
        trace_steps.append({
            "step": 6,
            "phase": "HUMAN_CHOICE",
            "signal": "chosen_scenario_id",
            "observed_value": chosen_scenario_id,
            "baseline_value": "ACT-CONTINUE",
            "interpretation": f"Operator selected {chosen_scenario_id} to bypass truck queue and recover shift buffer.",
        })

    return trace_steps
