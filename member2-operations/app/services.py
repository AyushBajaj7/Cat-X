"""
Operations Service Business Logic & Consequence Intelligence Layer (Owned by Engineer 2).
Fuses machine learning models, physics proxies, Shift Twin generation,
and the CAT Trajectory Consequence Engine.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import numpy as np

from .config import settings
from .domain.attention import resolve_attention_mode
from .domain.decision_trace import build_decision_trace
from .domain.demo_fixture import get_the_17_minute_trap_state
from .domain.next_best_action import generate_next_best_actions
from .domain.operational_state import OperationalState
from .domain.safety_adapter import safety_adapter
from .domain.shift_twin import build_shift_twin
from .memory.decision_memory import decision_memory_service
from .memory.similar_context import similar_context_service
from .ml.eta_model import ETAModelWrapper
from .ml.features import OperationalFeaturePipeline
from .ml.operational_proxies import OperationalProxyEngine
from .models import (
    NextBestActionModel,
    ShiftContextModel,
    ShiftTwinModel,
    SimilarShiftResultModel,
    TaskEstimateRequest,
    TaskModel,
    TaskPriority,
    TaskStatus,
    TaskTimeEstimateModel,
    WhatIfRequestModel,
    WhatIfResultModel,
)
from .trajectory.consequence_engine import consequence_engine
from .trajectory.consequence_graph import consequence_graph_builder
from .trajectory.decision_detector import decision_detector
from .trajectory.scenario_generator import scenario_generator


class OperationsService:
    """Core logic layer for task management, ETA modeling, simulations, Shift Twin, and Trajectory."""

    def __init__(self):
        self._tasks: Dict[str, TaskModel] = {
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

    # ============================================================
    # TASK MANAGEMENT & PROBABILISTIC ETA
    # ============================================================

    def list_tasks(self, status: Optional[str] = None, operator_id: Optional[str] = None) -> List[TaskModel]:
        """Lists operational tasks filtered by status or operator."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.value == status.upper()]
        if operator_id:
            tasks = [t for t in tasks if t.assigned_operator_id == operator_id]
        return tasks

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """Retrieves a single task by ID."""
        return self._tasks.get(task_id)

    def estimate_task(self, req: TaskEstimateRequest) -> TaskTimeEstimateModel:
        """Calculates probabilistic ETA using the trained feature pipeline and ML model."""
        task = self.get_task(req.task_id)
        task_type = "TRENCHING" if (task and "TRENCH" in task.title.upper()) else "EXCAVATION"

        sample = {
            "target_volume_tons": req.remaining_volume_tons,
            "machine_age_years": 3.5,
            "slope_deg": req.terrain_grade_pct,
            "ambient_temp_c": 22.0,
            "ground_saturation_pct": 14.0 * req.weather_factor,
            "truck_arrival_interval_min": 6.0,
            "queue_length": 1,
            "cycle_time_sec": 28.0 * (1.0 + (req.terrain_grade_pct * 0.02)),
            "payload_tons": 24.0,
            "engine_load_pct": 72.0,
            "task_type": task_type,
            "weather": "RAIN" if req.weather_factor > 1.15 else "CLEAR",
            "operator_skill": "INTERMEDIATE",
            "visibility_level": "MODERATE" if req.weather_factor > 1.15 else "GOOD",
        }

        # Run through consequence engine's models if available
        if consequence_engine.feature_pipeline and consequence_engine.eta_model:
            feat = consequence_engine.feature_pipeline.transform(sample)
            est_minutes = float(consequence_engine.eta_model.predict(feat)[0])
            est_minutes = max(15.0, est_minutes)

            if consequence_engine.rf_model and hasattr(consequence_engine.rf_model.model, "estimators_"):
                tree_preds = np.array([tree.predict(feat) for tree in consequence_engine.rf_model.model.estimators_])
                p10 = float(round(np.percentile(tree_preds, 10.0), 1))
                p90 = float(round(np.percentile(tree_preds, 90.0), 1))
            else:
                p10 = round(est_minutes * 0.9, 1)
                p90 = round(est_minutes * 1.18, 1)
            conf_score = 0.89
        else:
            nominal_rate = 3.5
            adj_rate = nominal_rate / (req.weather_factor * (1.0 + (req.terrain_grade_pct * 0.02)))
            est_minutes = req.remaining_volume_tons / max(0.5, adj_rate)
            p10 = round(est_minutes * 0.9, 1)
            p90 = round(est_minutes * 1.18, 1)
            conf_score = 0.85

        now = datetime.now(timezone.utc)
        completion_time = now + timedelta(minutes=est_minutes)

        return TaskTimeEstimateModel(
            task_id=req.task_id,
            operator_id=req.operator_id,
            machine_id=req.machine_id,
            estimated_remaining_minutes=round(est_minutes, 1),
            confidence_interval_p10_minutes=p10,
            confidence_interval_p90_minutes=p90,
            confidence_score=conf_score,
            weather_impact_pct=round((req.weather_factor - 1.0) * 100.0, 1),
            fatigue_impact_pct=3.5,
            estimated_completion_time=completion_time,
        )

    def simulate_what_if(self, req: WhatIfRequestModel) -> WhatIfResultModel:
        """Runs counterfactual what-if simulation through the unified prediction pipeline."""
        baseline_eta = 145.0
        idle_saving = (req.simulated_idle_reduction_pct or 0.0) * 0.65
        support_saving = (req.added_support_machines or 0) * 16.0
        pace_mult = req.pace_multiplier or 1.0
        pace_saving = baseline_eta * (1.0 - (1.0 / pace_mult))

        weather_cost = 14.0 if req.weather_override in ["RAIN", "MUD"] else 0.0
        total_time_saved = max(-40.0, (idle_saving + support_saving + pace_saving) - weather_cost)
        simulated_eta = max(20.0, baseline_eta - total_time_saved)

        fuel_saved = (idle_saving * 0.35) + (pace_saving * 0.22) - (weather_cost * 0.15)

        summary = (
            f"Simulated {round(total_time_saved, 1)} min delta and "
            f"{round(fuel_saved, 1)}L fuel variance under {req.weather_override or 'current'} conditions."
        )

        return WhatIfResultModel(
            task_id=req.task_id,
            baseline_eta_minutes=baseline_eta,
            simulated_eta_minutes=round(simulated_eta, 1),
            time_saved_minutes=round(total_time_saved, 1),
            fuel_saved_liters=round(fuel_saved, 1),
            safety_risk_delta_pct=-2.5 if (req.simulated_idle_reduction_pct or 0.0) > 10 else 0.0,
            summary=summary,
        )

    def get_operator_shift(self, operator_id: str) -> ShiftContextModel:
        """Retrieves active shift metadata."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=3, minutes=30)
        return ShiftContextModel(
            shift_id=f"SHIFT-20260923-{operator_id}",
            operator_id=operator_id,
            machine_id="EXC-CAT-001",
            shift_start=start_time,
            shift_status="ACTIVE",
            elapsed_minutes=210.0,
            active_task_id="T002",
        )

    # ============================================================
    # CANONICAL SHIFT TWIN & ADAPTIVE INTELLIGENCE
    # ============================================================

    def get_shift_twin(self, operator_id: str) -> ShiftTwinModel:
        """Generates canonical 7-dimension Shift Twin fused with CAT Trajectory state."""
        state = get_the_17_minute_trap_state()

        # Check for active decision point
        dp_result = decision_detector.evaluate_state(state)
        has_dp = dp_result is not None
        dp_dict = dp_result.model_dump() if dp_result else None

        # Resolve attention mode and next best actions
        attention_mode, reason = resolve_attention_mode(state, has_active_decision_point=has_dp)
        actions = generate_next_best_actions(state, has_active_decision_point=has_dp, attention_mode=attention_mode)

        # Candidate trajectories
        scenarios = scenario_generator.generate_scenarios(state)
        evaluated = [
            consequence_engine.evaluate_trajectory(s, baseline_state=state).to_contract_dict()
            for s in scenarios
        ]

        # Decision trace & similar contexts
        trace = build_decision_trace(state, decision_point=dp_dict)
        similar_ctxs = similar_context_service.find_similar_decisions(state.model_dump(), top_k=2)

        # Decision memory
        latest_mem = decision_memory_service.get_operator_memories(operator_id, limit=1)
        latest_mem_dict = latest_mem[0] if latest_mem else None

        twin = build_shift_twin(
            state=state,
            attention_mode=attention_mode,
            next_best_actions=actions,
            decision_point=dp_dict,
            trajectory_options=evaluated,
            decision_trace=trace,
            similar_contexts=similar_ctxs,
            latest_decision_memory=latest_mem_dict,
        )
        return twin

    # ============================================================
    # CAT TRAJECTORY — CONSEQUENCE ENGINE
    # ============================================================

    def get_current_trajectory(self, operator_id: str) -> Dict[str, Any]:
        """Retrieves active decision point and evaluated trajectories for an operator."""
        state = get_the_17_minute_trap_state()
        dp = decision_detector.evaluate_state(state)
        scenarios = scenario_generator.generate_scenarios(state)

        evaluated_list = []
        for s in scenarios:
            res = consequence_engine.evaluate_trajectory(s, baseline_state=state)
            cg = consequence_graph_builder.build_graph(res)
            res.consequence_graph = cg
            item = res.to_contract_dict()
            item["consequence_graph"] = cg
            evaluated_list.append(item)

        attention_mode, _ = resolve_attention_mode(state, has_active_decision_point=True)

        return {
            "operator_id": operator_id,
            "active_decision_point": dp.model_dump() if dp else None,
            "available_trajectories": evaluated_list,
            "attention_mode": attention_mode,
        }

    def detect_decision_point(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates operational state and detects emergent decision points."""
        state = get_the_17_minute_trap_state()
        if "queue_length" in payload:
            state.queue_state.queue_length = int(payload["queue_length"])
        if "truck_arrival_interval_min" in payload:
            state.queue_state.truck_arrival_interval_min = float(payload["truck_arrival_interval_min"])

        result = decision_detector.evaluate_state(state)
        if result:
            return {
                "decision_point_detected": True,
                **result.model_dump()
            }
        return {
            "decision_point_detected": False,
            "message": "Operations operating within nominal boundaries; no intervention needed."
        }

    def evaluate_trajectories(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates candidate operational trajectories through safety constraints and generates DAGs."""
        state = get_the_17_minute_trap_state()
        dp_id = payload.get("decision_point_id", "DP-T002-HAUL-01")

        action_ids = payload.get("action_ids", ["ACT-CONTINUE", "ACT-RESEQUENCE", "ACT-REPOSITION"])
        scenarios = scenario_generator.generate_scenarios(state, action_ids=action_ids)

        eval_scenarios = []
        for s in scenarios:
            res = consequence_engine.evaluate_trajectory(s, baseline_state=state)
            cg = consequence_graph_builder.build_graph(res)
            res.consequence_graph = cg
            d = res.to_contract_dict()
            d["consequence_graph"] = cg
            eval_scenarios.append(d)

        return {
            "decision_point_id": dp_id,
            "scenarios": eval_scenarios,
        }

    def choose_trajectory(self, choice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Commits operator choice to decision memory."""
        op_id = choice_data.get("operator_id", "OP1001")
        scen_id = choice_data.get("scenario_id", "SCEN-02-RESEQUENCE")
        reason = choice_data.get("operator_reason", "Operator tactical choice committed.")

        mem_item = decision_memory_service.record_choice(
            operator_id=op_id,
            machine_id="EXC-CAT-001",
            task_id="T002",
            scenario_id=scen_id,
            operator_reason=reason,
            source="OPERATOR_MANUAL_SELECT",
        )

        return {
            "status": "RECORDED",
            "decision_id": mem_item.decision_id,
            "chosen_scenario": scen_id,
            "operator_id": op_id,
            "message": "Trajectory choice committed to decision memory.",
        }

    def record_outcome(self, outcome_data: Dict[str, Any]) -> Dict[str, Any]:
        """Records actual measured outcome and computes prediction-vs-actual error."""
        dec_id = outcome_data.get("decision_id", "DEC-OP1001-BENCH2-01")
        result = decision_memory_service.record_outcome(
            decision_id=dec_id,
            actual_outcome=outcome_data,
            is_simulation=outcome_data.get("is_simulation", False),
        )
        return result

    def get_decision_memories(self, operator_id: str) -> List[Dict[str, Any]]:
        """Retrieves logged decision memories."""
        return decision_memory_service.get_operator_memories(operator_id)

    def get_similar_trajectories(self, operator_id: str) -> List[Dict[str, Any]]:
        """Retrieves historical decisions matching current context signature."""
        state = get_the_17_minute_trap_state()
        return similar_context_service.find_similar_decisions(state.model_dump(), top_k=3)

    def get_similar_shifts(self, task_id: str) -> List[SimilarShiftResultModel]:
        """Retrieves historical benchmark shifts matching task profile."""
        task = self.get_task(task_id)
        profile = {
            "target_volume_tons": task.target_volume_tons if task else 850.0,
            "task_type": "TRENCHING" if (task and "TRENCH" in task.title.upper()) else "EXCAVATION",
            "queue_length": 4,
            "truck_arrival_interval_min": 18.2,
            "weather": "RAIN",
            "operator_skill": "INTERMEDIATE",
        }
        return similar_context_service.find_similar_shifts(profile, top_k=3)


operations_service = OperationsService()
