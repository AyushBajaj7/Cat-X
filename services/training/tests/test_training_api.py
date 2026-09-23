"""Pytest test suite for Training Service REST API (Port 8003)."""

import pytest
from fastapi.testclient import TestClient
from services.training.app.main import app

client = TestClient(app)


def test_health_check():
    """Verify training service health check returns 200 and HEALTHY."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "training-service"
    assert data["port"] == 8003


def test_list_modules():
    """Verify module listing endpoint."""
    response = client.get("/api/v1/training/modules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    mod = data[0]
    assert "module_id" in mod
    assert "title" in mod
    assert "difficulty" in mod


def test_get_single_module():
    """Verify single module retrieval."""
    response = client.get("/api/v1/training/modules/MOD-SAF-01")
    assert response.status_code == 200
    data = response.json()
    assert data["module_id"] == "MOD-SAF-01"
    assert data["category"] == "SAFETY"


def test_get_nonexistent_module():
    """Verify 404 for invalid module ID."""
    response = client.get("/api/v1/training/modules/INVALID-MOD")
    assert response.status_code == 404


def test_get_recommendations():
    """Verify personalized recommendation retrieval."""
    response = client.get("/api/v1/training/recommendations/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    rec = data[0]
    assert "recommendation_id" in rec
    assert "module_id" in rec
    assert rec["operator_id"] == "OP1001"


def test_record_attempt():
    """Verify recording of training simulator attempt."""
    payload = {
        "operator_id": "OP1001",
        "module_id": "MOD-SAF-01",
        "score_pct": 92.5,
        "time_spent_seconds": 450,
        "feedback": "Perfect perimeter scanning.",
    }
    response = client.post("/api/v1/training/attempts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["attempt_id"].startswith("ATT-")
    assert data["passed"] is True
    assert data["score_pct"] == 92.5


def test_get_progress():
    """Verify operator cumulative progress retrieval."""
    response = client.get("/api/v1/training/progress/OP1001")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP1001"
    assert data["completed_modules_count"] >= 1
    assert "certifications_earned" in data
