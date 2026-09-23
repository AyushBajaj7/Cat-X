import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Clean cached 'app' modules to avoid collisions in monorepo test runners
for key in list(sys.modules.keys()):
    if key == "app" or key.startswith("app."):
        del sys.modules[key]

service_dir = str(Path(__file__).resolve().parent.parent)
if service_dir in sys.path:
    sys.path.remove(service_dir)
sys.path.insert(0, service_dir)

from app.main import app

client = TestClient(app)


def test_gateway_health():
    """Verify gateway health check returns 200 and downstreams are tracked."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "api-gateway"
    assert data["port"] == 8080
    assert "downstream" in data


def test_gateway_telemetry_fanout():
    """Verify telemetry ingestion endpoint accepts events with 202 status."""
    payload = {
        "event_id": "EVT-GW-001",
        "timestamp": "2026-09-23T07:30:00Z",
        "machine_id": "EXC001",
        "operator_id": "OP1001",
        "machine": {
            "engine_rpm": 1800.0,
            "engine_temp_c": 85.0,
            "hydraulic_pressure_kpa": 22000.0,
            "fuel_rate_lph": 17.0,
            "speed_kmh": 4.5
        },
        "operator": {
            "seatbelt_fastened": True,
            "fatigue_score": 15.0
        }
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "ACCEPTED"


def test_gateway_dashboard_composition():
    """Verify dashboard aggregation combines Shift Twin and Safety status."""
    response = client.get("/api/v1/dashboard/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert "shift_twin_summary" in data
    assert "immediate_safety_status" in data
    assert "top_training_recommendation" in data


def test_gateway_shift_twin_retrieval():
    """Verify direct Shift Twin endpoint on Gateway."""
    response = client.get("/api/v1/shift/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert "twin_id" in data
    assert "shift_health_score" in data


def test_gateway_demo_reset_and_states():
    """Verify demo reset and step stepping on Gateway."""
    res = client.post("/api/v1/demo/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "RESET_SUCCESSFUL"
    assert res.json()["current_step"] == 1

    # Step to step 5 (Decision point)
    res5 = client.post("/api/v1/demo/step", json={"step": 5})
    assert res5.status_code == 200
    data5 = res5.json()
    assert data5["current_step"] == 5
    assert data5["attention_mode"] == "DECISION_FOCUS"
    assert data5["decision_point"] is not None

    # Step to step 6 (Trajectory comparison)
    res6 = client.post("/api/v1/demo/step", json={"step": 6})
    assert res6.status_code == 200
    data6 = res6.json()
    assert len(data6["scenarios"]) >= 3
    # Check constraint rejection
    rejected = [s for s in data6["scenarios"] if s["constraint_status"] == "REJECTED"]
    assert len(rejected) >= 1
    assert "REJECTED" in rejected[0]["rejection_reason"]

    # Choose trajectory
    choose_res = client.post("/api/v1/trajectory/choose", json={
        "operator_id": "OP1001",
        "scenario_id": "SCEN-02-RESEQUENCE",
        "operator_reason": "Bypassed haul truck queue before rain onset."
    })
    assert choose_res.status_code == 200
    assert choose_res.json()["status"] == "RECORDED"

    # Outcome replay
    outcome_res = client.post("/api/v1/trajectory/outcome", json={"decision_id": "DEC-OP1001-001"})
    assert outcome_res.status_code == 200
    assert "prediction_error" in outcome_res.json()

    # Step 10: Similar Context
    res10 = client.post("/api/v1/demo/step", json={"step": 10})
    assert res10.status_code == 200
    assert res10.json()["similar_context"] is not None
    assert "SIMILAR SITUATION FOUND" in res10.json()["similar_context"]["banner"]

    # Reset back to pristine State 1
    reset_again = client.post("/api/v1/demo/reset")
    assert reset_again.json()["current_step"] == 1


def test_gateway_tasks_endpoints():
    """Verify task endpoints through Gateway."""
    res = client.get("/api/v1/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 1

    t002 = client.get("/api/v1/tasks/T002")
    assert t002.status_code == 200
    assert t002.json()["task_id"] == "T002"

    estimate_res = client.post("/api/v1/tasks/estimate", json={"task_id": "T002"})
    assert estimate_res.status_code == 200
    assert "estimated_remaining_minutes" in estimate_res.json()

    whatif_res = client.post("/api/v1/tasks/what-if", json={"simulated_idle_reduction_pct": 20.0})
    assert whatif_res.status_code == 200
    assert whatif_res.json()["time_saved_minutes"] > 0


def test_gateway_safety_endpoints():
    """Verify safety endpoints through Gateway."""
    st = client.get("/api/v1/safety/status/OP1001")
    assert st.status_code == 200
    assert "seatbelt_fastened" in st.json()

    alerts = client.get("/api/v1/safety/alerts/OP1001")
    assert alerts.status_code == 200
    assert isinstance(alerts.json(), list)

    bh = client.get("/api/v1/safety/behaviour/OP1001")
    assert bh.status_code == 200
    bh_data = bh.json()
    assert "idle_percentage" in bh_data or "analysis_id" in bh_data


def test_gateway_training_endpoints():
    """Verify training endpoints through Gateway."""
    mods = client.get("/api/v1/training/modules")
    assert mods.status_code == 200
    assert len(mods.json()) >= 4

    single = client.get("/api/v1/training/modules/SAFE_START_01")
    assert single.status_code == 200
    assert single.json()["module_id"] == "SAFE_START_01"

    recs = client.get("/api/v1/training/recommendations/OP1001")
    assert recs.status_code == 200
    assert len(recs.json()) >= 1

    attempt = client.post("/api/v1/training/attempts", json={
        "operator_id": "OP1001",
        "module_id": "SAFE_START_01",
        "score": 90.0,
        "max_score": 100.0,
        "mistakes": 1,
    })
    assert attempt.status_code == 201
    assert attempt.json()["percentage"] == 90.0
    assert attempt.json()["passed"] is True

    prog = client.get("/api/v1/training/progress/OP1001")
    assert prog.status_code == 200
    assert "completed_modules_count" in prog.json()

