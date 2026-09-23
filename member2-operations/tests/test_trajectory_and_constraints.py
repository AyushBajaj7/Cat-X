"""
Unit Tests for CAT Trajectory Decision-Point Detector, Scenario Generator,
Safety Constraints, and Consequence Graph (DAG).
"""

from pathlib import Path
import sys
import unittest

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
if str(OPERATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(OPERATIONS_DIR))

from app.domain.demo_fixture import get_the_17_minute_trap_state
from app.trajectory.consequence_engine import consequence_engine
from app.trajectory.consequence_graph import consequence_graph_builder
from app.trajectory.decision_detector import decision_detector
from app.trajectory.safety_constraints import safety_constraint_engine
from app.trajectory.scenario_generator import scenario_generator


class TestTrajectoryAndConstraints(unittest.TestCase):
    """Test suite for CAT Trajectory components."""

    def setUp(self):
        self.state = get_the_17_minute_trap_state()

    def test_decision_point_detector_triggers_on_trap(self):
        """Verify detector catches the 17-minute trap queue imbalance."""
        dp = decision_detector.evaluate_state(self.state)
        self.assertIsNotNone(dp)
        self.assertEqual(dp.trigger_type, "QUEUE_IMBALANCE")
        self.assertEqual(dp.severity, "HIGH")
        self.assertIn("ACT-RESEQUENCE", dp.available_actions)
        self.assertIn("queue_length", dp.evidence)

    def test_decision_point_detector_critical_safety(self):
        """Verify detector assigns CRITICAL severity when safety perimeter breached."""
        unsafe_state = get_the_17_minute_trap_state()
        unsafe_state.safety_signals.active_proximity_hazards = 2
        unsafe_state.environment.slope_deg = 14.8

        dp = decision_detector.evaluate_state(unsafe_state)
        self.assertIsNotNone(dp)
        self.assertEqual(dp.trigger_type, "SAFETY_APPROACH")
        self.assertEqual(dp.severity, "CRITICAL")

    def test_scenario_generator_creates_3_alternatives(self):
        """Verify scenario generator produces Continue, Resequence, and Reposition."""
        scenarios = scenario_generator.generate_scenarios(self.state)
        self.assertEqual(len(scenarios), 3)

        action_ids = [s.action_id for s in scenarios]
        self.assertIn("ACT-CONTINUE", action_ids)
        self.assertIn("ACT-RESEQUENCE", action_ids)
        self.assertIn("ACT-REPOSITION", action_ids)

        # Verify state cloning isolation
        resequence_scen = next(s for s in scenarios if s.action_id == "ACT-RESEQUENCE")
        self.assertLess(resequence_scen.transformed_state.queue_state.queue_length, self.state.queue_state.queue_length)
        # Original state untouched
        self.assertEqual(self.state.queue_state.queue_length, 4)

    def test_safety_constraint_engine_hard_rejection(self):
        """Verify violated hard constraint marks scenario REJECTED, not merely penalized."""
        # Test extreme slope > 15.0 deg
        res = safety_constraint_engine.validate_scenario(
            scenario_id="SCEN-TEST-UNSAFE",
            state=self.state,
            overrides={"slope_deg": 16.5},
        )
        self.assertEqual(res.constraint_status, "REJECTED")
        self.assertGreaterEqual(res.composite_safety_risk_score, 85.0)
        self.assertTrue(any("Slope 16.5° exceeds" in r for r in res.rejection_reasons))

        # Test proximity violation < 10.0m
        res_prox = safety_constraint_engine.validate_scenario(
            scenario_id="SCEN-TEST-PROX",
            state=self.state,
            overrides={"proximity_distance_m": 6.0},
        )
        self.assertEqual(res_prox.constraint_status, "REJECTED")

        # Test feasible slope
        res_safe = safety_constraint_engine.validate_scenario(
            scenario_id="SCEN-TEST-SAFE",
            state=self.state,
            overrides={"slope_deg": 6.5, "proximity_distance_m": 25.0},
        )
        self.assertEqual(res_safe.constraint_status, "FEASIBLE")

    def test_consequence_engine_evaluates_scenarios(self):
        """Verify consequence engine produces model-derived outcomes for all scenarios."""
        scenarios = scenario_generator.generate_scenarios(self.state)
        for s in scenarios:
            res = consequence_engine.evaluate_trajectory(s, baseline_state=self.state)
            self.assertIn("eta_minutes", res.predicted_outcome)
            self.assertIn("fuel_liters", res.predicted_outcome)
            self.assertIn("safety_risk_score", res.predicted_outcome)
            self.assertIn(res.constraint_status, ["FEASIBLE", "REJECTED"])

    def test_consequence_graph_dag_structure(self):
        """Verify consequence graph generates valid DAG nodes and edges."""
        scenarios = scenario_generator.generate_scenarios(self.state)
        resequence_scen = next(s for s in scenarios if s.action_id == "ACT-RESEQUENCE")
        res = consequence_engine.evaluate_trajectory(resequence_scen, baseline_state=self.state)

        cg = consequence_graph_builder.build_graph(res)
        self.assertTrue(cg["graph_id"].startswith("CG-"))
        self.assertEqual(cg["root_action"], "ACT-RESEQUENCE")

        # Node check
        nodes = cg["nodes"]
        self.assertGreaterEqual(len(nodes), 4)
        node_types = [n["type"] for n in nodes]
        self.assertIn("DECISION", node_types)
        self.assertIn("OUTCOME", node_types)

        # Edge check
        edges = cg["edges"]
        self.assertGreaterEqual(len(edges), 3)
        for edge in edges:
            self.assertIn(edge["relationship"], ["CAUSES", "INCREASES", "DECREASES", "CONTRIBUTES_TO", "LEADS_TO", "REDUCES"])


if __name__ == "__main__":
    unittest.main()
