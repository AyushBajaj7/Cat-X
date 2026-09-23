"""Deterministic constraint generator for CAT Trajectory engine."""

from datetime import datetime, timedelta, timezone
from typing import List
from ..config import settings
from ..models import (
    AlertSeverity,
    ConstraintSignal,
    ConstraintStatus,
    ProximityWarningLevel,
    TelemetryEventInput,
)
from .seatbelt_rule import SeatbeltEvaluationResult
from .proximity_rule import ProximityEvaluationResult
from .combined_hazard_rule import CombinedHazardResult
from .idle_rule import IdleEvaluationResult


class ConstraintGenerator:
    """
    Translates safety rule evaluations into explainable operational constraint
    signals consumed by the CAT Trajectory engine (Engineer 2).
    """

    def generate_constraints(
        self,
        event: TelemetryEventInput,
        seatbelt_res: SeatbeltEvaluationResult,
        proximity_res: ProximityEvaluationResult,
        combined_res: CombinedHazardResult,
        idle_res: IdleEvaluationResult,
    ) -> List[ConstraintSignal]:
        constraints: List[ConstraintSignal] = []
        now = datetime.now(timezone.utc)
        ts_str = int(now.timestamp())

        # 1. Proximity constraints: Speed limitation or position hold
        if proximity_res.warning_level == ProximityWarningLevel.CRITICAL:
            constraints.append(
                ConstraintSignal(
                    signal_id=f"CST-PROX-CRIT-{event.operator_id}-{ts_str}",
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    timestamp=now,
                    constraint_type="SPEED_LIMIT",
                    status=ConstraintStatus.ACTIVE,
                    severity=AlertSeverity.CRITICAL,
                    rationale=f"Personnel or obstacle breach at {proximity_res.distance_meters:.1f}m (< {settings.proximity_critical_m}m). Incursion in danger envelope.",
                    recommended_action="IMMEDIATE_HOLD_POSITION",
                    evidence={
                        "max_permitted_speed_mps": 0.0,
                        "current_proximity_distance_m": proximity_res.distance_meters,
                        "critical_threshold_m": settings.proximity_critical_m,
                        "prune_trajectory_branches": ["CONTINUE_CYCLE", "TRAM_FORWARD", "AGGRESSIVE_SWING"],
                    },
                    expires_at=now + timedelta(minutes=5),
                )
            )
        elif proximity_res.warning_level == ProximityWarningLevel.HIGH:
            constraints.append(
                ConstraintSignal(
                    signal_id=f"CST-PROX-HIGH-{event.operator_id}-{ts_str}",
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    timestamp=now,
                    constraint_type="SPEED_LIMIT",
                    status=ConstraintStatus.ACTIVE,
                    severity=AlertSeverity.HIGH,
                    rationale=f"Proximity buffer hazard ({proximity_res.distance_meters:.1f}m). Restrict movement speed.",
                    recommended_action="REDUCE_SPEED_CREEP_MODE",
                    evidence={
                        "max_permitted_speed_mps": 1.0,
                        "current_proximity_distance_m": proximity_res.distance_meters,
                        "high_threshold_m": settings.proximity_high_m,
                        "prune_trajectory_branches": ["HIGH_SPEED_TRAMMING"],
                    },
                    expires_at=now + timedelta(minutes=3),
                )
            )

        # 2. Seatbelt constraint: Movement interlock
        if not seatbelt_res.is_compliant:
            constraints.append(
                ConstraintSignal(
                    signal_id=f"CST-SB-LOCK-{event.operator_id}-{ts_str}",
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    timestamp=now,
                    constraint_type="OPERATOR_PAUSE",
                    status=ConstraintStatus.ACTIVE,
                    severity=AlertSeverity.HIGH,
                    rationale="Operator seatbelt unfastened. Kinetic machine movement disallowed.",
                    recommended_action="FASTEN_SEATBELT_BEFORE_CYCLE",
                    evidence={
                        "seatbelt_fastened": False,
                        "compliance_pct": seatbelt_res.compliance_pct,
                        "prune_trajectory_branches": ["INITIATE_CYCLE", "TRAMMING"],
                    },
                    expires_at=now + timedelta(minutes=2),
                )
            )

        # 3. Combined Hazard: Supervisor clearance required
        if combined_res.is_combined_hazard:
            constraints.append(
                ConstraintSignal(
                    signal_id=f"CST-COMBINED-HOLD-{event.operator_id}-{ts_str}",
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    timestamp=now,
                    constraint_type="SUPERVISOR_INTERVENTION",
                    status=ConstraintStatus.ACTIVE,
                    severity=AlertSeverity.CRITICAL,
                    rationale=f"Multiple concurrent violations ({', '.join(combined_res.contributing_factors)}). Operational safety envelope breached.",
                    recommended_action="SUSPEND_TASK_AWAIT_SUPERVISOR",
                    evidence={
                        "contributing_factors": combined_res.contributing_factors,
                        "prune_trajectory_branches": ["ALL_AUTONOMOUS_ACTIONS", "TASK_ADVANCE"],
                    },
                    expires_at=now + timedelta(minutes=15),
                )
            )

        # 4. Excessive Idle constraint: Task hold / Engine shutdown advisory
        if idle_res.is_excessive and idle_res.idle_minutes >= settings.idle_critical_minutes:
            constraints.append(
                ConstraintSignal(
                    signal_id=f"CST-IDLE-HOLD-{event.operator_id}-{ts_str}",
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    timestamp=now,
                    constraint_type="TASK_HOLD",
                    status=ConstraintStatus.ACTIVE,
                    severity=AlertSeverity.LOW,
                    rationale=f"Extended idle duration ({idle_res.idle_minutes:.1f}m). Fuel waste optimization required.",
                    recommended_action="REASSIGN_DISPATCH_OR_SHUTDOWN",
                    evidence={
                        "idle_minutes": idle_res.idle_minutes,
                        "fuel_wasted_l": idle_res.fuel_wasted_l,
                        "prune_trajectory_branches": ["PROLONGED_STANDSTILL"],
                    },
                    expires_at=now + timedelta(minutes=10),
                )
            )

        return constraints
