"""
CAT Trajectory — Decision-Point Detector & Severity Engine.
Detects discrete operational inflection points using transparent deterministic rules.
Filters routine telemetry; triggers only when operator intervention has high tactical leverage.
Conforms strictly to shared/contracts/decision-point.schema.json.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from ..domain.operational_state import OperationalState


class DecisionPointDetectionResult(BaseModel):
    """Output contract for detected operational decision points."""
    decision_point_id: str
    timestamp: str
    operator_id: str
    machine_id: str
    task_id: str
    trigger_type: str
    severity: str
    summary: str
    evidence: Dict[str, Any]
    available_actions: List[str]


class DecisionPointDetector:
    """Deterministic rule-based operational inflection point detector."""

    def __init__(
        self,
        queue_threshold: int = 3,
        truck_gap_threshold_min: float = 12.0,
        delay_risk_threshold_min: float = 10.0,
        idle_excess_threshold_pct: float = 15.0,
        slope_warning_threshold_deg: float = 12.0,
        proximity_warning_dist_m: float = 15.0,
    ):
        self.queue_threshold = queue_threshold
        self.truck_gap_threshold_min = truck_gap_threshold_min
        self.delay_risk_threshold_min = delay_risk_threshold_min
        self.idle_excess_threshold_pct = idle_excess_threshold_pct
        self.slope_warning_threshold_deg = slope_warning_threshold_deg
        self.proximity_warning_dist_m = proximity_warning_dist_m

    def evaluate_state(self, state: OperationalState) -> Optional[DecisionPointDetectionResult]:
        """Evaluates operational state and returns detected decision point if thresholds are breached."""
        # Calculate key derived operational signals
        scheduled_minutes = state.current_task.estimated_duration_minutes
        projected_minutes = state.task_progress.elapsed_minutes + state.prediction_state.estimated_remaining_minutes
        projected_delay_min = max(0.0, projected_minutes - scheduled_minutes)

        queue_len = state.queue_state.queue_length
        arrival_interval = state.queue_state.truck_arrival_interval_min
        idle_pct = state.idle_state.idle_percentage
        slope = state.environment.slope_deg
        saturation = state.environment.ground_saturation_pct
        weather = state.environment.weather_condition
        active_hazards = state.safety_signals.active_proximity_hazards
        anomaly_detected = state.behaviour_signals.anomaly_detected

        now_iso = datetime.now(timezone.utc).isoformat()
        op_id = state.operator.operator_id
        mach_id = state.machine.machine_id
        task_id = state.current_task.task_id

        # 1. Check Safety Approach (CRITICAL / HIGH priority)
        if active_hazards > 0 or slope >= self.slope_warning_threshold_deg or not state.safety_signals.seatbelt_status:
            severity = "CRITICAL" if (active_hazards > 1 or slope >= 14.5 or not state.safety_signals.seatbelt_status) else "HIGH"
            summary = (
                f"Machine operating near safety perimeter: slope at {slope:.1f}° "
                f"with {active_hazards} proximity flags."
            )
            evidence = {
                "slope_deg": slope,
                "slope_limit_deg": 15.0,
                "active_hazards": active_hazards,
                "seatbelt_status": state.safety_signals.seatbelt_status,
                "safety_score": state.safety_signals.safety_score,
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-SAFE-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="SAFETY_APPROACH",
                severity=severity,
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-REPOSITION", "ACT-REVIEW-SAFETY"],
            )

        # 2. Check Queue Imbalance (e.g. The 17-Minute Trap)
        if queue_len >= self.queue_threshold or arrival_interval >= self.truck_gap_threshold_min:
            severity = "HIGH" if projected_delay_min >= self.delay_risk_threshold_min else "MEDIUM"
            summary = (
                f"Haul fleet arrival mismatch: {queue_len} trucks queued with "
                f"{arrival_interval:.1f} min gap, creating low-idle delay trap."
            )
            evidence = {
                "queue_length": queue_len,
                "truck_arrival_interval_min": arrival_interval,
                "current_idle_pct": idle_pct,
                "ground_saturation_pct": saturation,
                "weather_condition": weather,
                "baseline_eta_delay_minutes": round(projected_delay_min, 1),
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-HAUL-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="QUEUE_IMBALANCE",
                severity=severity,
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-RESEQUENCE", "ACT-REPOSITION"],
            )

        # 3. Check Shift Delay Risk
        if projected_delay_min >= self.delay_risk_threshold_min:
            severity = "HIGH" if projected_delay_min >= 20.0 else "MEDIUM"
            summary = (
                f"Projected task completion delayed by {projected_delay_min:.1f} minutes past shift handoff."
            )
            evidence = {
                "scheduled_duration_minutes": scheduled_minutes,
                "projected_duration_minutes": round(projected_minutes, 1),
                "delay_minutes": round(projected_delay_min, 1),
                "pace_ratio": state.task_progress.pace_ratio,
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-SCHED-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="SHIFT_DELAY_RISK",
                severity=severity,
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-RESEQUENCE", "ACT-REPOSITION"],
            )

        # 4. Check Efficiency Deviation (Excessive low idle)
        if idle_pct >= self.idle_excess_threshold_pct:
            summary = f"Excavator low idle reached {idle_pct:.1f}%, exceeding 15% efficiency benchmark."
            evidence = {
                "idle_pct": idle_pct,
                "idle_minutes": state.idle_state.idle_minutes,
                "wasted_fuel_litres": state.idle_state.idle_fuel_wasted_litres,
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-EFF-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="EFFICIENCY_DEVIATION",
                severity="MEDIUM",
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-RESEQUENCE"],
            )

        # 5. Check Environment Change (Incoming rain / saturation surge)
        if weather in ["RAIN", "MUD"] and saturation >= 25.0:
            summary = f"Weather change ({weather}) elevated ground saturation to {saturation:.1f}%."
            evidence = {
                "weather": weather,
                "ground_saturation_pct": saturation,
                "ambient_temp_c": state.environment.ambient_temp_c,
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-ENV-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="ENVIRONMENT_CHANGE",
                severity="MEDIUM",
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-REPOSITION"],
            )

        # 6. Check Unusual Operating Pattern
        if anomaly_detected or state.behaviour_signals.aggressive_maneuver_count > 2:
            summary = "Irregular slew or bucket shock load detected in current dig cycle."
            evidence = {
                "aggressive_events": state.behaviour_signals.aggressive_maneuver_count,
                "cycle_consistency_pct": state.behaviour_signals.cycle_consistency_pct,
                "flags": state.behaviour_signals.flags,
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-ANOM-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="UNUSUAL_OPERATING_PATTERN",
                severity="MEDIUM",
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-REVIEW-SAFETY"],
            )

        # 7. Check Task Transition
        if state.task_progress.pct_complete >= 95.0:
            summary = "Task nearing completion (95%+ volume moved). Prepare next assignment transition."
            evidence = {
                "completed_volume_tons": state.current_task.completed_volume_tons,
                "target_volume_tons": state.current_task.target_volume_tons,
                "pct_complete": state.task_progress.pct_complete,
            }
            return DecisionPointDetectionResult(
                decision_point_id=f"DP-{task_id}-TRANS-01",
                timestamp=now_iso,
                operator_id=op_id,
                machine_id=mach_id,
                task_id=task_id,
                trigger_type="TASK_TRANSITION",
                severity="LOW",
                summary=summary,
                evidence=evidence,
                available_actions=["ACT-CONTINUE", "ACT-TRANSITION"],
            )

        # Nominal operation: no decision point
        return None


decision_detector = DecisionPointDetector()
