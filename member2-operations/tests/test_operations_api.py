"""
Comprehensive Integration & Contract Test Suite for Operations Service REST API.
Verifies all 14 endpoints adhering strictly to /shared/contracts/.
Compatible with both pytest and python -m unittest.
"""

from pathlib import Path
import sys
import unittest
from fastapi.testclient import TestClient

# Path resolution
service_dir = str(Path(__file__).resolve().parent.parent)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from app.main import app

client = TestClient(app)


class TestOperationsAPI(unittest.TestCase):
    """Test suite covering task, estimation, shift twin, and trajectory endpoints."""

    def test_01_health_check(self):
        """Verify health check returns 200 and HEALTHY."""
        res = client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["service"], "operations-service")
        self.assertEqual(data["port"], 8002)

    def test_02_list_tasks(self):
        """Verify listing tasks returns array of tasks."""
        res = client.get("/api/v1/tasks")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)
        task = data[0]
        self.assertIn("task_id", task)
        self.assertIn("target_volume_tons", task)
        self.assertIn("status", task)

    def test_03_get_single_task(self):
        """Verify single task lookup by ID."""
        res = client.get("/api/v1/tasks/T002")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["task_id"], "T002")
        self.assertEqual(data["priority"], "CRITICAL")

    def test_04_get_nonexistent_task(self):
        """Verify 404 for unknown task ID."""
        res = client.get("/api/v1/tasks/UNKNOWN_TASK_999")
        self.assertEqual(res.status_code, 404)

    def test_05_task_time_estimate(self):
        """Verify probabilistic task ETA estimation endpoint."""
        payload = {
            "task_id": "T002",
            "operator_id": "OP1001",
            "machine_id": "EXC-CAT-001",
            "remaining_volume_tons": 530.0,
            "weather_factor": 1.15,
            "terrain_grade_pct": 3.5,
        }
        res = client.post("/api/v1/tasks/estimate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["task_id"], "T002")
        self.assertGreater(data["estimated_remaining_minutes"], 0)
        self.assertIn("estimated_completion_time", data)
        self.assertGreaterEqual(data["confidence_score"], 0.0)
        self.assertLessEqual(data["confidence_score"], 1.0)
        self.assertIsNotNone(data["confidence_interval_p10_minutes"])
        self.assertIsNotNone(data["confidence_interval_p90_minutes"])

    def test_06_what_if_simulation(self):
        """Verify counterfactual what-if simulation endpoint."""
        payload = {
            "task_id": "T002",
            "operator_id": "OP1001",
            "simulated_idle_reduction_pct": 18.0,
            "added_support_machines": 1,
            "pace_multiplier": 1.15,
        }
        res = client.post("/api/v1/tasks/what-if", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["task_id"], "T002")
        self.assertGreater(data["time_saved_minutes"], 0)
        self.assertIn("summary", data)

    def test_07_get_operator_shift(self):
        """Verify operator shift context endpoint."""
        res = client.get("/api/v1/operator/OP1001/shift")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["operator_id"], "OP1001")
        self.assertEqual(data["shift_status"], "ACTIVE")

    def test_08_get_canonical_shift_twin(self):
        """Verify canonical 7-dimension Shift Twin representation."""
        res = client.get("/api/v1/operator/OP1001/shift-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["operator_id"], "OP1001")
        self.assertIn("environment", data)
        self.assertIn("safety", data)
        self.assertIn("behaviour", data)
        self.assertIn("productivity", data)
        self.assertIn("prediction", data)
        self.assertIn("next_best_actions", data)
        self.assertIn("shift_forecast", data)
        self.assertIn("attention_mode", data)
        self.assertGreaterEqual(len(data["next_best_actions"]), 1)

    def test_09_similar_shifts(self):
        """Verify historical benchmark shift retrieval."""
        res = client.get("/api/v1/tasks/T002/similar-shifts")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("similarity_score_pct", data[0])

    def test_10_trajectory_current_state(self):
        """Verify current trajectory state returns active decision point and evaluated options."""
        res = client.get("/api/v1/trajectory/current/OP1001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["operator_id"], "OP1001")
        self.assertIn("active_decision_point", data)
        self.assertIn("available_trajectories", data)
        self.assertEqual(data["attention_mode"], "DECISION_FOCUS")

    def test_11_trajectory_detect(self):
        """Verify trajectory decision-point detector endpoint."""
        res = client.post("/api/v1/trajectory/detect", json={
            "operator_id": "OP1001",
            "queue_length": 4,
            "truck_arrival_interval_min": 18.2,
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["decision_point_detected"])
        self.assertEqual(data["trigger_type"], "QUEUE_IMBALANCE")
        self.assertIn(data["severity"], ["HIGH", "CRITICAL"])

    def test_12_trajectory_evaluate(self):
        """Verify candidate trajectory evaluation through safety constraints and DAGs."""
        res = client.post("/api/v1/trajectory/evaluate", json={"decision_point_id": "DP-T002-HAUL-01"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        scenarios = data["scenarios"]
        self.assertGreaterEqual(len(scenarios), 2)
        for s in scenarios:
            self.assertIn("scenario_id", s)
            self.assertIn("predicted_outcome", s)
            self.assertIn("constraint_status", s)
            self.assertIn(s["constraint_status"], ["FEASIBLE", "REJECTED"])
            self.assertIn("consequence_graph", s)
            cg = s["consequence_graph"]
            self.assertIn("nodes", cg)
            self.assertIn("edges", cg)

    def test_13_trajectory_choose(self):
        """Verify operator trajectory choice recording."""
        choice = {
            "operator_id": "OP1001",
            "decision_point_id": "DP-T002-HAUL-01",
            "scenario_id": "SCEN-02-RESEQUENCE",
            "operator_reason": "Bypassed haul truck queue before rain onset.",
        }
        res = client.post("/api/v1/trajectory/choose", json=choice)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "RECORDED")
        self.assertIn("decision_id", data)

    def test_14_trajectory_outcome(self):
        """Verify recording actual outcome and prediction-vs-actual error auditing."""
        outcome = {
            "decision_id": "DEC-OP1001-BENCH2-01",
            "actual_duration_minutes": 144.0,
            "actual_fuel_litres": 167.5,
            "actual_idle_minutes": 4.0,
        }
        res = client.post("/api/v1/trajectory/outcome", json=outcome)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "EVALUATED")
        self.assertIn("prediction_error", data)
        self.assertIn("drift_status", data)

    def test_15_trajectory_memory_retrieval(self):
        """Verify retrieving decision memory for operator."""
        res = client.get("/api/v1/trajectory/memory/OP1001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_16_trajectory_similar_retrieval(self):
        """Verify retrieving similar historical decisions."""
        res = client.get("/api/v1/trajectory/similar/OP1001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        self.assertIn("similarity_score_pct", data[0])


if __name__ == "__main__":
    unittest.main()
