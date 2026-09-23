"""
End-to-End Unit Scenario Test: CAT Trajectory Closed Loop.
Exercises the exact end-to-end operational sequence mandated by the architecture:
Current State
  -> Decision Point Detection
  -> 3 Candidate Scenarios Generation
  -> Reject Unsafe Scenario via Hard Safety Constraints
  -> Evaluate Feasible Scenarios through ML & Proxies
  -> Consequence Graph (DAG) Construction
  -> Operator Trajectory Choice
  -> Simulate Outcome & Compute Prediction Error
  -> Store in Decision Memory
  -> Retrieve Similar Context for Future Decisions
"""

from pathlib import Path
import sys
import unittest

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
if str(OPERATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(OPERATIONS_DIR))

from app.domain.demo_fixture import get_the_17_minute_trap_state
from app.domain.attention import resolve_attention_mode
from app.domain.next_best_action import generate_next_best_actions
from app.memory.decision_memory import decision_memory_service
from app.memory.similar_context import similar_context_service
from app.trajectory.consequence_engine import consequence_engine
from app.trajectory.consequence_graph import consequence_graph_builder
from app.trajectory.decision_detector import decision_detector
from app.trajectory.safety_constraints import safety_constraint_engine
from app.trajectory.scenario_generator import scenario_generator


class TestE2ETrajectoryClosedLoop(unittest.TestCase):
    """Full end-to-end closed loop unit scenario test."""

    def test_complete_trajectory_lifecycle(self):
        # ----------------------------------------------------
        # 1. OBSERVE: Current State ("The 17-Minute Trap")
        # ----------------------------------------------------
        initial_state = get_the_17_minute_trap_state()
        self.assertEqual(initial_state.operator.operator_id, "OP1001")
        self.assertEqual(initial_state.queue_state.queue_length, 4)
        self.assertEqual(initial_state.environment.weather_condition, "RAIN")

        # ----------------------------------------------------
        # 2. DETECT DECISION POINT
        # ----------------------------------------------------
        dp = decision_detector.evaluate_state(initial_state)
        self.assertIsNotNone(dp)
        self.assertEqual(dp.trigger_type, "QUEUE_IMBALANCE")
        self.assertEqual(dp.severity, "HIGH")

        # Verify Attention mode shifts to DECISION_FOCUS
        att_mode, att_reason = resolve_attention_mode(initial_state, has_active_decision_point=True)
        self.assertEqual(att_mode, "DECISION_FOCUS")

        # Next Best Actions suggest comparing trajectories
        nbas = generate_next_best_actions(initial_state, has_active_decision_point=True, attention_mode=att_mode)
        self.assertGreaterEqual(len(nbas), 1)

        # ----------------------------------------------------
        # 3. GENERATE 3 CANDIDATE ALTERNATIVES
        # ----------------------------------------------------
        candidate_scenarios = scenario_generator.generate_scenarios(initial_state)
        self.assertEqual(len(candidate_scenarios), 3)

        # ----------------------------------------------------
        # 4. REJECT UNSAFE SCENARIOS & EVALUATE FEASIBLE
        # ----------------------------------------------------
        # Let's test a fourth hypothetically unsafe scenario (e.g. steep 16.5° shortcut)
        unsafe_scen = candidate_scenarios[0].model_copy(deep=True)
        unsafe_scen.scenario_id = "SCEN-04-UNSAFE-SHORTCUT"
        unsafe_val = safety_constraint_engine.validate_scenario(
            scenario_id=unsafe_scen.scenario_id,
            state=unsafe_scen.transformed_state,
            overrides={"slope_deg": 16.8},  # Exceeds 15.0 limit
        )
        self.assertEqual(unsafe_val.constraint_status, "REJECTED")

        # Evaluate the 3 actual candidate scenarios
        evaluated_scenarios = []
        for scen in candidate_scenarios:
            res = consequence_engine.evaluate_trajectory(scen, baseline_state=initial_state)
            self.assertEqual(res.constraint_status, "FEASIBLE")
            evaluated_scenarios.append(res)

        self.assertEqual(len(evaluated_scenarios), 3)

        # ----------------------------------------------------
        # 5. CONSEQUENCE GRAPH (DAG)
        # ----------------------------------------------------
        resequence_res = next(r for r in evaluated_scenarios if r.action_id == "ACT-RESEQUENCE")
        cg = consequence_graph_builder.build_graph(resequence_res)
        self.assertIn("nodes", cg)
        self.assertIn("edges", cg)
        self.assertGreater(len(cg["nodes"]), 3)
        self.assertGreater(len(cg["edges"]), 2)

        # ----------------------------------------------------
        # 6. OPERATOR CHOOSES TRAJECTORY
        # ----------------------------------------------------
        chosen_scen = resequence_res
        decision_record = decision_memory_service.record_choice(
            operator_id="OP1001",
            machine_id="EXC-CAT-001",
            task_id="T002",
            scenario_id=chosen_scen.scenario_id,
            available_scenarios=[s.scenario_id for s in candidate_scenarios],
            predicted_outcome=chosen_scen.predicted_outcome,
            operator_reason="Pivoted to Bench 3 overburden to bypass crusher bottleneck before rain front.",
            context_signature="SIG-TRENCHING-RAIN-INTERMEDIATE-HIQUEUE",
            source="OPERATOR_MANUAL_SELECT",
        )
        self.assertIsNotNone(decision_record.decision_id)
        self.assertEqual(decision_record.chosen_scenario, chosen_scen.scenario_id)

        # ----------------------------------------------------
        # 7. SIMULATE / REPLAY OUTCOME & ERROR DRIFT
        # ----------------------------------------------------
        pred_eta = chosen_scen.predicted_outcome.get("eta_minutes", 45.0)
        pred_fuel = chosen_scen.predicted_outcome.get("fuel_liters", 32.0)
        simulated_actual_metrics = {
            "actual_duration_minutes": round(pred_eta + 1.2, 1),
            "actual_fuel_litres": round(pred_fuel - 0.5, 1),
            "actual_idle_minutes": 3.8,
            "completion_status": "COMPLETED_AHEAD_OF_SCHEDULE",
        }
        outcome_result = decision_memory_service.record_outcome(
            decision_id=decision_record.decision_id,
            actual_outcome=simulated_actual_metrics,
            is_simulation=True,
        )
        self.assertEqual(outcome_result["status"], "EVALUATED")
        self.assertIn("prediction_error", outcome_result)
        self.assertEqual(outcome_result["drift_status"], "WITHIN_TOLERANCE")

        # ----------------------------------------------------
        # 8. RETRIEVE DECISION MEMORY
        # ----------------------------------------------------
        memories = decision_memory_service.get_operator_memories("OP1001")
        self.assertGreaterEqual(len(memories), 1)
        logged_mem = next(m for m in memories if m["decision_id"] == decision_record.decision_id)
        self.assertIsNotNone(logged_mem["actual_outcome"])
        self.assertIsNotNone(logged_mem["prediction_error"])

        # ----------------------------------------------------
        # 9. REUSE DECISION MEMORY: SIMILAR CONTEXT
        # ----------------------------------------------------
        matching_precedents = similar_context_service.find_similar_decisions(
            initial_state.model_dump(), top_k=2
        )
        self.assertGreaterEqual(len(matching_precedents), 1)
        precedent = matching_precedents[0]
        self.assertIn("actual_time_saved_minutes", precedent)
        self.assertIn("chosen_action", precedent)
        self.assertEqual(precedent["chosen_action"], "RESEQUENCE")


if __name__ == "__main__":
    unittest.main()
