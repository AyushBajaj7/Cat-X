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


def test_health_check():
    """Verify safety service health check returns 200 and HEALTHY."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "safety-service"
    assert data["port"] == 8001


def test_safety_status_endpoint():
    """Verify safety status endpoint returns valid contract fields."""
    response = client.get("/api/v1/safety/status/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert "seatbelt_fastened" in data
    assert "overall_safety_score" in data
    assert data["overall_safety_score"] >= 0.0


def test_safety_alerts_endpoint():
    """Verify safety alerts listing endpoint."""
    response = client.get("/api/v1/safety/alerts/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    alert = data[0]
    assert "alert_id" in alert
    assert "severity" in alert
    assert "message" in alert


def test_safety_incidents_endpoint():
    """Verify safety incidents audit endpoint."""
    response = client.get("/api/v1/safety/incidents/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    incident = data[0]
    assert "incident_id" in incident
    assert "incident_type" in incident


def test_safety_behaviour_endpoint():
    """Verify behavior analysis endpoint."""
    response = client.get("/api/v1/safety/behaviour/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert "overall_behaviour_score" in data
    assert "excessive_idling_score" in data


def test_telemetry_ingestion():
    """Verify telemetry ingestion and immediate safety evaluation."""
    telemetry_payload = {
        "event_id": "EVT-TEST-001",
        "timestamp": "2026-09-23T07:30:00Z",
        "machine_id": "EXC001",
        "operator_id": "OP1001",
        "machine": {
            "engine_rpm": 1850.0,
            "engine_temp_c": 88.0,
            "hydraulic_pressure_kpa": 24000.0,
            "fuel_rate_lph": 18.5,
            "speed_kmh": 6.2,
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194
            }
        },
        "operator": {
            "seatbelt_fastened": True,
            "fatigue_score": 22.0
        }
    }
    response = client.post("/api/v1/safety/telemetry", json=telemetry_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert data["seatbelt_fastened"] is True
    assert data["overall_safety_score"] > 80.0
