"""Pytest test suite for Operations Service REST API (Port 8002)."""

import pytest
from fastapi.testclient import TestClient
from services.operations.app.main import app

client = TestClient(app)


def test_health_check():
    """Verify operations service health check returns 200 and HEALTHY."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "operations-service"
    assert data["port"] == 8002


def test_list_tasks():
    """Verify task listing endpoint returns valid tasks."""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    task = data[0]
    assert "task_id" in task
    assert "target_volume_tons" in task
    assert "status" in task


def test_get_single_task():
    """Verify single task retrieval by ID."""
    response = client.get("/api/v1/tasks/T002")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "T002"
    assert data["priority"] == "CRITICAL"


def test_get_nonexistent_task():
    """Verify 404 on nonexistent task ID."""
    response = client.get("/api/v1/tasks/NONEXISTENT_999")
    assert response.status_code == 404


def test_task_time_estimation():
    """Verify probabilistic task ETA estimation endpoint."""
    payload = {
        "task_id": "T002",
        "operator_id": "OP1001",
        "machine_id": "EXC001",
        "remaining_volume_tons": 530.0,
        "weather_factor": 1.10,
        "terrain_grade_pct": 3.0,
    }
    response = client.post("/api/v1/tasks/estimate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "T002"
    assert data["estimated_remaining_minutes"] > 0
    assert "estimated_completion_time" in data
    assert 0.0 <= data["confidence_score"] <= 1.0


def test_what_if_simulation():
    """Verify what-if simulation endpoint."""
    payload = {
        "task_id": "T002",
        "operator_id": "OP1001",
        "simulated_idle_reduction_pct": 15.0,
        "added_support_machines": 1,
        "pace_multiplier": 1.1,
    }
    response = client.post("/api/v1/tasks/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "T002"
    assert data["time_saved_minutes"] > 0
    assert data["fuel_saved_liters"] > 0
    assert "summary" in data


def test_get_operator_shift():
    """Verify shift context endpoint."""
    response = client.get("/api/v1/operator/OP1001/shift")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert data["shift_status"] == "ACTIVE"


def test_get_canonical_shift_twin():
    """Verify the 7-dimensional Shift Twin representation endpoint."""
    response = client.get("/api/v1/operator/OP1001/shift-twin")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert "environment" in data
    assert "safety" in data
    assert "behaviour" in data
    assert "productivity" in data
    assert "prediction" in data
    assert "next_best_actions" in data
    assert len(data["next_best_actions"]) >= 1


def test_similar_shifts():
    """Verify historical similar shift retrieval."""
    response = client.get("/api/v1/tasks/T002/similar-shifts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "similarity_score_pct" in data[0]
