"""
CAT Trajectory — Deterministic Demo Fixture: "The 17-Minute Trap".
Accurately replicates the operational dilemma documented in docs/DEMO_SCENARIO.md:
- Task: T002 (Bench 2 Deep Trenching & Excavation, 850 tons target, 320 tons completed)
- Machine: EXC-CAT-001 (Caterpillar 349 Hydraulic Excavator)
- Operator: OP1001 (Intermediate Experience Tier)
- Dilemma: 4 haul trucks bunched, 18.2-minute gap impending, rain front rising,
  and 17.4-minute completion delay past 14:00 shift handoff.

Critical Architecture Rule: Predictions and consequence graphs are evaluated LIVE
through trained ML models and proxy engines—NEVER hardcoded.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from .operational_state import (
    BehaviourSignals,
    EnvironmentState,
    IdleState,
    MachineInfo,
    MachineState,
    OperationalState,
    OperatorInfo,
    PredictionState,
    ProductivityState,
    QueueState,
    SafetySignals,
    TaskInfo,
    TaskProgress,
)


def get_the_17_minute_trap_state(now: datetime = None) -> OperationalState:
    """Returns deterministic initial state for 'The 17-Minute Trap' scenario."""
    now = now or datetime.now(timezone.utc)
    scheduled_start = now - timedelta(hours=3, minutes=30)  # 210 minutes elapsed

    scheduled_duration = 240.0  # 4 hours
    completed_tons = 320.0
    target_tons = 850.0
    remaining_tons = target_tons - completed_tons

    return OperationalState(
        timestamp=now,
        operator=OperatorInfo(
            operator_id="OP1001",
            name="Shift Operator OP1001",
            experience_tier="INTERMEDIATE",
            total_operating_hours=1450.0,
        ),
        machine=MachineInfo(
            machine_id="EXC-CAT-001",
            model="CAT-349D",
            category="EXCAVATOR",
            payload_capacity_tons=28.0,
            status="OPERATIONAL",
        ),
        current_task=TaskInfo(
            task_id="T002",
            title="Bench 2 Trenching & Trench Grading",
            site_zone="BENCH_2_WEST",
            target_volume_tons=target_tons,
            completed_volume_tons=completed_tons,
            status="IN_PROGRESS",
            priority="CRITICAL",
            estimated_duration_minutes=scheduled_duration,
        ),
        task_progress=TaskProgress(
            pct_complete=round((completed_tons / target_tons) * 100.0, 1),
            volume_remaining_tons=remaining_tons,
            elapsed_minutes=210.0,
            pace_ratio=0.88,
        ),
        environment=EnvironmentState(
            weather_condition="RAIN",
            ambient_temp_c=18.0,
            ground_saturation_pct=28.0,
            visibility_level="MODERATE",
            slope_deg=7.5,
        ),
        queue_state=QueueState(
            queue_length=4,
            truck_arrival_interval_min=18.2,
            trucks_in_transit=4,
            bottleneck_severity="SEVERE",
        ),
        machine_state=MachineState(
            engine_rpm=1800.0,
            engine_load_pct=68.0,
            hydraulic_pressure_bar=320.0,
            swing_angle_deg=48.0,
            fuel_rate_lph=34.0,
        ),
        idle_state=IdleState(
            idle_minutes=42.0,
            idle_percentage=14.8,
            high_idle_flag=True,
            idle_fuel_wasted_litres=5.8,
        ),
        productivity_state=ProductivityState(
            tons_per_hour=91.4,
            cycle_time_sec=34.0,
            bucket_fill_factor=0.88,
            efficiency_rating="DEGRADED",
        ),
        safety_signals=SafetySignals(
            seatbelt_status=True,
            seatbelt_compliance_pct=99.2,
            active_proximity_hazards=0,
            safety_score=96.0,
            constraint_flags=[],
        ),
        behaviour_signals=BehaviourSignals(
            excessive_idling_score=14.8,
            aggressive_maneuver_count=0,
            cycle_consistency_pct=88.0,
            overall_behaviour_score=92.0,
            anomaly_detected=False,
            flags=["HAUL_CYCLE_MISMATCH", "APPROACHING_IDLE_LIMIT"],
        ),
        prediction_state=PredictionState(
            estimated_remaining_minutes=47.4,  # 210 + 47.4 = 257.4 min (+17.4 min delay)
            estimated_completion_time=now + timedelta(minutes=47.4),
            delay_probability_pct=88.5,
            confidence_score=0.91,
            lower_minutes=42.0,
            upper_minutes=54.0,
        ),
    )
