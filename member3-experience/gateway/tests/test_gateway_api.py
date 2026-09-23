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
