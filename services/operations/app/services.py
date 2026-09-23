"""Operations Service business logic & Shift Twin engine skeleton (Owned by Engineer 2)."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from .models import (
    NextBestActionModel,
    ShiftContextModel,
    ShiftTwinBehaviour,
    ShiftTwinEnvironment,
    ShiftTwinModel,
    ShiftTwinPrediction,
    ShiftTwinProductivity,
    ShiftTwinSafety,
    SimilarShiftResultModel,
    TaskEstimateRequest,
    TaskModel,
    TaskPriority,
    TaskStatus,
    TaskTimeEstimateModel,
    WhatIfRequestModel,
    WhatIfResultModel,
)


class OperationsService:
    """Core logic layer for task management, ETA modeling, simulations, and Shift Twin generation."""

    def __init__(self):
        self._tasks: dict[str, TaskModel] = {
            "T001": TaskModel(
                task_id="T001",
                title="Excavation Zone 4 - Overburden Removal",
                description="Excavate 500 tons of surface overburden on North Ridge.",
                site_zone="ZONE_4_NORTH",
                target_volume_tons=500.0,
                completed_volume_tons=500.0,
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.HIGH,
                estimated_duration_minutes=180.0,
                actual_duration_minutes=172.0,
                assigned_operator_id="OP1001",
                assigned_machine_id="EXC-CAT-001",
            ),
            "T002": TaskModel(
                task_id="T002",
                title="Bench 2 Trenching & Trench Grading",
                description="Deep trenching for stormwater pipeline bypass.",
                site_zone="BENCH_2_WEST",
                target_volume_tons=850.0,
                completed_volume_tons=320.0,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.CRITICAL,
                estimated_duration_minutes=240.0,
                actual_duration_minutes=95.0,
                assigned_operator_id="OP1001",
                assigned_machine_id="EXC-CAT-001",
            ),
            "T003": TaskModel(
                task_id="T003",
                title="Stockpile 1 Loading to Haul Fleet",
                description="Load processed aggregate into 740 GC Articulated Trucks.",
                site_zone="STOCKPILE_1",
                target_volume_tons=1200.0,
                completed_volume_tons=0.0,
                status=TaskStatus.PENDING,
                priority=TaskPriority.NORMAL,
                estimated_duration_minutes=300.0,
                actual_duration_minutes=0.0,
                assigned_operator_id="OP1001",
                assigned_machine_id="EXC-CAT-001",
            ),
        }

    def list_tasks(self, status: Optional[str] = None, operator_id: Optional[str] = None) -> List[TaskModel]:
        """List tasks optionally filtered by status or operator."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        if operator_id:
            tasks = [t for t in tasks if t.assigned_operator_id == operator_id]
        return tasks

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """Retrieve single task by ID."""
        return self._tasks.get(task_id)

    def estimate_task(self, req: TaskEstimateRequest) -> TaskTimeEstimateModel:
        """Calculate probabilistic ETA based on remaining volume, weather, and grade."""
        nominal_rate = 3.5
        adjusted_rate = nominal_rate / (req.weather_factor * (1.0 + (req.terrain_grade_pct * 0.02)))
        est_minutes = req.remaining_volume_tons / max(0.5, adjusted_rate)

        now = datetime.now(timezone.utc)
        completion_time = now + timedelta(minutes=est_minutes)

        return TaskTimeEstimateModel(
            task_id=req.task_id,
            operator_id=req.operator_id,
            machine_id=req.machine_id,
            estimated_remaining_minutes=round(est_minutes, 1),
            confidence_interval_p10_minutes=round(est_minutes * 0.9, 1),
            confidence_interval_p90_minutes=round(est_minutes * 1.18, 1),
            confidence_score=0.88,
            weather_impact_pct=round((req.weather_factor - 1.0) * 100, 1),
            fatigue_impact_pct=3.5,
            estimated_completion_time=completion_time,
        )

    def simulate_what_if(self, req: WhatIfRequestModel) -> WhatIfResultModel:
        """Run what-if simulation evaluating parameter impacts on shift outcome."""
        baseline_eta = 145.0
        idle_saving = (req.simulated_idle_reduction_pct or 0.0) * 0.6
        support_saving = (req.added_support_machines or 0) * 18.0
        pace_multiplier = req.pace_multiplier or 1.0
        pace_saving = baseline_eta * (1.0 - (1.0 / pace_multiplier))

        total_saved = idle_saving + support_saving + pace_saving
        simulated_eta = max(20.0, baseline_eta - total_saved)
        fuel_saved = (idle_saving * 0.35) + (pace_saving * 0.2)

        return WhatIfResultModel(
            task_id=req.task_id,
            baseline_eta_minutes=baseline_eta,
            simulated_eta_minutes=round(simulated_eta, 1),
            time_saved_minutes=round(total_saved, 1),
            fuel_saved_liters=round(fuel_saved, 1),
            safety_risk_delta_pct=-2.5 if (req.simulated_idle_reduction_pct or 0.0) > 10 else 0.0,
            summary=f"Simulated reduction of idle and pace optimization yields {round(total_saved, 1)} minutes saved and {round(fuel_saved, 1)}L fuel reduction.",
        )

    def get_operator_shift(self, operator_id: str) -> ShiftContextModel:
        """Retrieve operator active shift metadata."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=3, minutes=45)
        return ShiftContextModel(
            shift_id=f"SHIFT-20260923-{operator_id}",
            operator_id=operator_id,
            machine_id="EXC-CAT-001",
            shift_start=start_time,
            shift_status="ACTIVE",
            elapsed_minutes=225.0,
            active_task_id="T002",
        )

    def get_shift_twin(self, operator_id: str) -> ShiftTwinModel:
        """Generate canonical CAT Operator Shift Twin representation fusing all 7 dimensions."""
        now = datetime.now(timezone.utc)
        return ShiftTwinModel(
            twin_id=f"TWIN-{operator_id}-LIVE",
            operator_id=operator_id,
            machine_id="EXC-CAT-001",
            current_task_id="T002",
            updated_at=now,
            shift_health_score=94.2,
            environment=ShiftTwinEnvironment(
                weather_condition="CLEAR",
                ambient_temp_c=24.5,
                ground_saturation_pct=14.0,
                visibility_level="EXCELLENT",
            ),
            safety=ShiftTwinSafety(
                seatbelt_status=True,
                seatbelt_compliance_pct=99.2,
                active_proximity_hazards=0,
                safety_score=97.5,
            ),
            behaviour=ShiftTwinBehaviour(
                idle_percentage=11.4,
                aggressive_events_count=0,
                fatigue_risk_level="LOW",
                behaviour_score=93.0,
            ),
            productivity=ShiftTwinProductivity(
                completed_volume_tons=820.0,
                target_volume_tons=1350.0,
                pace_percentage=104.5,
                efficiency_rating="OPTIMAL",
            ),
            prediction=ShiftTwinPrediction(
                estimated_completion_time=now + timedelta(hours=2, minutes=30),
                estimated_remaining_minutes=150.0,
                delay_probability_pct=4.8,
                confidence_score=0.91,
            ),
            next_best_actions=[
                NextBestActionModel(
                    action_id="NBA-01",
                    title="Optimize Bench 2 Swing Angle",
                    rationale="Swing cycle is currently 48 degrees; re-spotting haul truck reduces swing to 32 degrees.",
                    category="EFFICIENCY",
                    priority="HIGH",
                    estimated_benefit="Saves ~18 minutes and 6.4L fuel over remaining volume.",
                ),
                NextBestActionModel(
                    action_id="NBA-02",
                    title="Prepare for Shift Midpoint Walkaround",
                    rationale="3.5 continuous operating hours logged; inspect hydraulic hose fittings on boom pivot.",
                    category="MAINTENANCE",
                    priority="NORMAL",
                    estimated_benefit="Prevents unscheduled hydraulic pressure drop.",
                ),
            ],
        )

    def get_similar_shifts(self, task_id: str) -> List[SimilarShiftResultModel]:
        """Retrieve benchmark shifts from historical data matching machine and task profile."""
        return [
            SimilarShiftResultModel(
                shift_id="HIST-SH-8842",
                similarity_score_pct=94.5,
                operator_tier="EXPERT",
                machine_model="CAT-349D",
                actual_duration_minutes=218.0,
                total_volume_tons=860.0,
                fuel_efficiency_tons_per_liter=38.2,
                safety_score=99.0,
                key_takeaways=[
                    "Early haul truck queue management cut idle by 14%",
                    "Kept trench face slope at 1:1 to prevent material slumping",
                ],
            ),
            SimilarShiftResultModel(
                shift_id="HIST-SH-7911",
                similarity_score_pct=88.0,
                operator_tier="INTERMEDIATE",
                machine_model="CAT-349D",
                actual_duration_minutes=242.0,
                total_volume_tons=840.0,
                fuel_efficiency_tons_per_liter=34.8,
                safety_score=95.0,
                key_takeaways=[
                    "Wet ground conditions caused 18-minute transit delay on Ramp 3",
                ],
            ),
        ]


operations_service = OperationsService()
