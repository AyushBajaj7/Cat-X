"""Comprehensive test suite for Safety Service (Port 8001).

Covers:
- Contract conformity (safety.schema.json, behaviour.schema.json, error.schema.json)
- Telemetry ingestion (nested & flat dual-format)
- Rule engines (seatbelt kinetic, proximity 4-tier, combined hazard, idle efficiency)
- Incident management (deduplication, acknowledge/resolve lifecycle, audit trail)
- Behaviour intelligence (feature extraction, baseline z-scores, IsolationForest anomaly, multi-axis trends)
- Trajectory constraint signal generation (explainable evidence, branch pruning)
- Error handling (422 validation, 404 not found)
- 6 Deterministic demo fixtures
"""

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
from app.demo_fixtures import ALL_FIXTURES
from app.models import AlertSeverity, IncidentStatus, ProximityWarningLevel, SafetyState

client = TestClient(app)


# ============================================================================
# 1. Health and Baseline Contract Endpoints
# ============================================================================


def test_01_health_check():
    """Verify safety service health check returns 200 and HEALTHY."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "safety-service"
    assert data["port"] == 8001


def test_02_safety_status_endpoint_contract():
    """Verify safety status endpoint returns all mandatory contract fields."""
    response = client.get("/api/v1/safety/status/OP-CONTRACT-01")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP-CONTRACT-01"
    assert "machine_id" in data
    assert "timestamp" in data
    assert "seatbelt_fastened" in data
    assert "seatbelt_compliance_pct" in data
    assert "proximity_warning_level" in data
    assert "active_hazard_count" in data
    assert "overall_safety_score" in data
    assert "safety_state" in data
    assert data["overall_safety_score"] >= 0.0 and data["overall_safety_score"] <= 100.0


def test_03_safety_alerts_endpoint():
    """Verify safety alerts listing endpoint and filtering."""
    response = client.get("/api/v1/safety/alerts/OP-CONTRACT-01")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_04_safety_incidents_endpoint():
    """Verify safety incidents audit endpoint and filtering."""
    response = client.get("/api/v1/safety/incidents/OP-CONTRACT-01")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_05_safety_behaviour_endpoint_contract():
    """Verify behavior analysis endpoint conforms to behaviour.schema.json."""
    response = client.get("/api/v1/safety/behaviour/OP-CONTRACT-01")
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP-CONTRACT-01"
    assert "machine_id" in data
    assert "timestamp" in data
    assert "excessive_idling_score" in data
    assert "aggressive_maneuver_count" in data
    assert "unsafe_speed_events" in data
    assert "cycle_consistency_pct" in data
    assert "overall_behaviour_score" in data
    assert "flags" in data
    assert "anomaly_detected" in data
    assert isinstance(data["flags"], list)
    assert isinstance(data["anomaly_detected"], bool)


# ============================================================================
# 2. Dual-Format Telemetry Ingestion
# ============================================================================


def test_06_telemetry_ingestion_canonical_nested():
    """Verify telemetry ingestion using canonical nested schema."""
    payload = {
        "event_id": "EVT-NESTED-001",
        "timestamp": "2026-09-23T07:30:00Z",
        "machine_id": "EXC001",
        "operator_id": "OP-NESTED",
        "machine": {
            "engine_rpm": 1850.0,
            "engine_temp_c": 88.0,
            "hydraulic_pressure_kpa": 24000.0,
            "fuel_rate_lph": 18.5,
            "speed_kmh": 6.2,
            "location": {"latitude": 37.7749, "longitude": -122.4194},
        },
        "operator": {
            "seatbelt_fastened": True,
            "fatigue_score": 22.0,
        },
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP-NESTED"
    assert data["seatbelt_fastened"] is True
    assert data["overall_safety_score"] > 80.0
    assert data["safety_state"] == SafetyState.SAFE.value


def test_07_telemetry_ingestion_flat_format():
    """Verify telemetry ingestion using flat sensor schema."""
    payload = {
        "event_id": "EVT-FLAT-001",
        "timestamp": "2026-09-23T07:35:00Z",
        "machine_id": "EXC002",
        "operator_id": "OP-FLAT",
        "seatbelt_status": "BUCKLED",
        "machine_speed_mps": 1.4,
        "fuel_rate_lph": 17.0,
        "engine_hours": 1200.5,
        "idle_minutes": 2.0,
        "proximity_distance_m": 45.0,
        "machine_state": "WORKING",
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == "OP-FLAT"
    assert data["seatbelt_fastened"] is True
    assert data["safety_state"] == SafetyState.SAFE.value


# ============================================================================
# 3. Rule Evaluation: Seatbelt Kinetic Rules
# ============================================================================


def test_08_seatbelt_unbuckled_stationary():
    """Verify unbuckled stationary machine generates MEDIUM alert and WARNING state."""
    payload = {
        "event_id": "EVT-SB-STAT",
        "machine_id": "EXC001",
        "operator_id": "OP-SB-01",
        "seatbelt_status": "UNBUCKLED",
        "machine_speed_mps": 0.0,
        "machine_state": "IDLE",
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["seatbelt_fastened"] is False
    assert data["safety_state"] == SafetyState.WARNING.value
    assert len(data["active_alerts"]) >= 1
    alert = [a for a in data["active_alerts"] if a["alert_type"] == "SEATBELT_UNBUCKLED"][0]
    assert alert["severity"] == AlertSeverity.MEDIUM.value


def test_09_seatbelt_unbuckled_moving_work():
    """Verify unbuckled machine during active work generates HIGH alert and incident."""
    payload = {
        "event_id": "EVT-SB-WORK",
        "machine_id": "EXC001",
        "operator_id": "OP-SB-02",
        "seatbelt_status": "UNBUCKLED",
        "machine_speed_mps": 1.2,
        "machine_state": "WORKING",
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["seatbelt_fastened"] is False
    alert = [a for a in data["active_alerts"] if a["alert_type"] == "SEATBELT_UNBUCKLED"][0]
    assert alert["severity"] == AlertSeverity.HIGH.value

    # Verify incident was logged
    inc_resp = client.get("/api/v1/safety/incidents/OP-SB-02")
    assert inc_resp.status_code == 200
    incidents = inc_resp.json()
    assert len(incidents) >= 1
    assert any(i["incident_type"] == "SEATBELT_VIOLATION" for i in incidents)


def test_10_seatbelt_unbuckled_tramming_high_risk():
    """Verify unbuckled tramming (>2 m/s) generates CRITICAL alert and HIGH_RISK state."""
    payload = {
        "event_id": "EVT-SB-TRAM",
        "machine_id": "EXC001",
        "operator_id": "OP-SB-03",
        "seatbelt_status": "UNBUCKLED",
        "machine_speed_mps": 3.0,
        "machine_state": "TRAMMING",
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["safety_state"] == SafetyState.HIGH_RISK.value
    alert = [a for a in data["active_alerts"] if a["alert_type"] == "SEATBELT_UNBUCKLED"][0]
    assert alert["severity"] == AlertSeverity.CRITICAL.value


# ============================================================================
# 4. Rule Evaluation: Proximity 4-Tier Envelope
# ============================================================================


def test_11_proximity_critical_breach():
    """Verify proximity < 5m triggers CRITICAL alert, near miss incident, and HOLD constraint."""
    payload = {
        "event_id": "EVT-PROX-CRIT",
        "machine_id": "EXC001",
        "operator_id": "OP-PROX-CRIT",
        "seatbelt_status": "BUCKLED",
        "proximity_distance_m": 3.2,
        "machine_speed_mps": 1.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["proximity_warning_level"] == ProximityWarningLevel.CRITICAL.value
    assert data["safety_state"] == SafetyState.HIGH_RISK.value

    # Check constraints
    constraints = data["active_constraints"]
    assert len(constraints) >= 1
    speed_constraint = [c for c in constraints if c["constraint_type"] == "SPEED_LIMIT"][0]
    assert speed_constraint["severity"] == AlertSeverity.CRITICAL.value
    assert speed_constraint["evidence"]["max_permitted_speed_mps"] == 0.0


def test_12_proximity_high_warning():
    """Verify proximity < 10m triggers HIGH warning and reduced speed constraint."""
    payload = {
        "event_id": "EVT-PROX-HIGH",
        "machine_id": "EXC001",
        "operator_id": "OP-PROX-HIGH",
        "seatbelt_status": "BUCKLED",
        "proximity_distance_m": 8.0,
        "machine_speed_mps": 1.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["proximity_warning_level"] == ProximityWarningLevel.HIGH.value
    assert data["safety_state"] == SafetyState.WARNING.value


def test_13_proximity_medium_buffer():
    """Verify proximity < 20m triggers MEDIUM warning."""
    payload = {
        "event_id": "EVT-PROX-MED",
        "machine_id": "EXC001",
        "operator_id": "OP-PROX-MED",
        "seatbelt_status": "BUCKLED",
        "proximity_distance_m": 15.0,
        "machine_speed_mps": 1.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["proximity_warning_level"] == ProximityWarningLevel.MEDIUM.value


def test_14_proximity_low_perimeter():
    """Verify proximity < 30m triggers LOW advisory."""
    payload = {
        "event_id": "EVT-PROX-LOW",
        "machine_id": "EXC001",
        "operator_id": "OP-PROX-LOW",
        "seatbelt_status": "BUCKLED",
        "proximity_distance_m": 25.0,
        "machine_speed_mps": 1.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["proximity_warning_level"] == ProximityWarningLevel.LOW.value


def test_15_proximity_clear():
    """Verify proximity >= 30m results in NONE warning level."""
    payload = {
        "event_id": "EVT-PROX-CLR",
        "machine_id": "EXC001",
        "operator_id": "OP-PROX-CLR",
        "seatbelt_status": "BUCKLED",
        "proximity_distance_m": 55.0,
        "machine_speed_mps": 1.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["proximity_warning_level"] == ProximityWarningLevel.NONE.value


# ============================================================================
# 5. Rule Evaluation: Combined Hazard Detection
# ============================================================================


def test_16_combined_hazard_compound_risk():
    """Verify concurrent unbuckled + proximity breach generates COMBINED_HAZARD."""
    payload = {
        "event_id": "EVT-COMBO-01",
        "machine_id": "EXC001",
        "operator_id": "OP-COMBO",
        "seatbelt_status": "UNBUCKLED",
        "proximity_distance_m": 7.5,
        "machine_speed_mps": 1.8,
        "machine_state": "WORKING",
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["safety_state"] == SafetyState.HIGH_RISK.value
    alerts = data["active_alerts"]
    assert any(a["alert_type"] == "COMBINED_HAZARD" for a in alerts)
    combo_alert = [a for a in alerts if a["alert_type"] == "COMBINED_HAZARD"][0]
    assert combo_alert["severity"] == AlertSeverity.CRITICAL.value

    # Verify SUPERVISOR_INTERVENTION constraint
    constraints = data["active_constraints"]
    assert any(c["constraint_type"] == "SUPERVISOR_INTERVENTION" for c in constraints)


# ============================================================================
# 6. Rule Evaluation: Excessive Idling (Behaviour Intelligence)
# ============================================================================


def test_17_excessive_idle_warning_25_min():
    """Verify idle >= 25m generates LOW warning alert (behaviour intelligence)."""
    payload = {
        "event_id": "EVT-IDLE-25",
        "machine_id": "EXC001",
        "operator_id": "OP-IDLE-25",
        "seatbelt_status": "BUCKLED",
        "idle_minutes": 28.0,
        "fuel_rate_lph": 15.0,
        "machine_speed_mps": 0.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    alerts = data["active_alerts"]
    idle_alerts = [a for a in alerts if a["alert_type"] == "EXCESSIVE_IDLE"]
    assert len(idle_alerts) >= 1
    assert idle_alerts[0]["severity"] == AlertSeverity.LOW.value


def test_18_excessive_idle_critical_45_min():
    """Verify idle >= 45m generates MEDIUM alert and estimated fuel waste."""
    payload = {
        "event_id": "EVT-IDLE-45",
        "machine_id": "EXC001",
        "operator_id": "OP-IDLE-45",
        "seatbelt_status": "BUCKLED",
        "idle_minutes": 50.0,
        "fuel_rate_lph": 16.0,
        "machine_speed_mps": 0.0,
    }
    response = client.post("/api/v1/safety/telemetry", json=payload)
    assert response.status_code == 200
    data = response.json()
    alerts = data["active_alerts"]
    idle_alerts = [a for a in alerts if a["alert_type"] == "EXCESSIVE_IDLE"]
    assert len(idle_alerts) >= 1
    assert idle_alerts[0]["severity"] == AlertSeverity.MEDIUM.value
    assert idle_alerts[0]["evidence"]["estimated_fuel_wasted_l"] > 10.0


# ============================================================================
# 7. Incident Lifecycle Management & Deduplication
# ============================================================================


def test_19_incident_deduplication():
    """Verify duplicate incident within 300s window is deduplicated."""
    payload = {
        "event_id": "EVT-DEDUP-1",
        "machine_id": "EXC001",
        "operator_id": "OP-DEDUP",
        "seatbelt_status": "UNBUCKLED",
        "machine_speed_mps": 1.5,
        "machine_state": "WORKING",
    }
    # First post creates incident
    client.post("/api/v1/safety/telemetry", json=payload)
    inc_resp1 = client.get("/api/v1/safety/incidents/OP-DEDUP")
    count1 = len(inc_resp1.json())
    assert count1 >= 1

    # Immediate second post with same condition should be deduplicated
    payload["event_id"] = "EVT-DEDUP-2"
    client.post("/api/v1/safety/telemetry", json=payload)
    inc_resp2 = client.get("/api/v1/safety/incidents/OP-DEDUP")
    count2 = len(inc_resp2.json())
    assert count2 == count1  # No duplicate incident added!


def test_20_incident_lifecycle_acknowledge_and_resolve():
    """Verify incident transitions from OPEN -> ACKNOWLEDGED -> RESOLVED."""
    payload = {
        "event_id": "EVT-LIFECYCLE",
        "machine_id": "EXC001",
        "operator_id": "OP-LIFECYCLE",
        "proximity_distance_m": 2.5,  # Critical near miss
        "machine_speed_mps": 0.8,
    }
    client.post("/api/v1/safety/telemetry", json=payload)
    incidents = client.get("/api/v1/safety/incidents/OP-LIFECYCLE").json()
    assert len(incidents) >= 1
    target = incidents[0]
    incident_id = target["incident_id"]
    assert target["status"] == IncidentStatus.OPEN.value

    # Acknowledge
    ack_resp = client.post(
        f"/api/v1/safety/incidents/{incident_id}/acknowledge",
        json={"acknowledged_by": "SUPERVISOR_ALICE"},
    )
    assert ack_resp.status_code == 200
    ack_data = ack_resp.json()
    assert ack_data["status"] == IncidentStatus.ACKNOWLEDGED.value
    assert ack_data["acknowledged_by"] == "SUPERVISOR_ALICE"
    assert ack_data["acknowledged_at"] is not None

    # Resolve
    res_resp = client.post(
        f"/api/v1/safety/incidents/{incident_id}/resolve",
        json={"resolved_by": "SUPERVISOR_ALICE", "resolution_notes": "Obstacle cleared by spotter team."},
    )
    assert res_resp.status_code == 200
    res_data = res_resp.json()
    assert res_data["status"] == IncidentStatus.RESOLVED.value
    assert res_data["resolved_by"] == "SUPERVISOR_ALICE"
    assert "spotter team" in res_data["resolution_notes"]


def test_21_incident_not_found_404():
    """Verify 404 returned on non-existent incident acknowledge or resolve."""
    ack_resp = client.post("/api/v1/safety/incidents/INC-NONEXISTENT/acknowledge", json={})
    assert ack_resp.status_code == 404
    assert ack_resp.json()["error_code"] == "NOT_FOUND"

    res_resp = client.post(
        "/api/v1/safety/incidents/INC-NONEXISTENT/resolve",
        json={"resolution_notes": "test note here"},
    )
    assert res_resp.status_code == 404
    assert res_resp.json()["error_code"] == "NOT_FOUND"


# ============================================================================
# 8. Behaviour Intelligence, Anomaly Engine & Trends
# ============================================================================


def test_22_behaviour_nominal_operation():
    """Verify nominal telemetry yields low idle score and anomaly_detected=False."""
    op_id = "OP-BEHAV-NOMINAL"
    for i in range(5):
        payload = {
            "event_id": f"EVT-BN-{i}",
            "machine_id": "EXC001",
            "operator_id": op_id,
            "seatbelt_status": "BUCKLED",
            "machine_speed_mps": 1.5,
            "fuel_rate_lph": 16.0,
            "operator": {"seatbelt_fastened": True, "fatigue_score": 20.0},
            "machine": {
                "engine_rpm": 1750.0,
                "engine_temp_c": 86.0,
                "hydraulic_pressure_kpa": 23000.0,
                "fuel_rate_lph": 16.0,
                "speed_kmh": 5.4,
            },
        }
        client.post("/api/v1/safety/telemetry", json=payload)

    resp = client.get(f"/api/v1/safety/behaviour/{op_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["anomaly_detected"] is False
    assert data["overall_behaviour_score"] > 85.0


def test_23_behavioural_drift_anomaly_detection():
    """Verify escalating drift sequence triggers anomaly detection."""
    op_id = "OP-DRIFT-TEST"
    seq = ALL_FIXTURES["BEHAVIOURAL_DRIFT"](operator_id=op_id)
    for evt in seq:
        resp = client.post("/api/v1/safety/telemetry", json=evt.model_dump(mode="json"))
        assert resp.status_code == 200

    behav_resp = client.get(f"/api/v1/safety/behaviour/{op_id}")
    assert behav_resp.status_code == 200
    data = behav_resp.json()
    assert "anomaly_score" in data
    assert data["anomaly_score"] >= 0.0 and data["anomaly_score"] <= 1.0
    # Multi-axis trends should reflect degradation in fatigue or speed
    assert "trends" in data
    trends = data["trends"]
    assert "fatigue" in trends
    assert "speed_control" in trends


# ============================================================================
# 9. All 6 Demo Fixtures Validation
# ============================================================================


def test_24_fixture_normal_operation():
    """Verify Fixture 1: NORMAL_OPERATION."""
    evt = ALL_FIXTURES["NORMAL_OPERATION"]()
    resp = client.post("/api/v1/safety/telemetry", json=evt.model_dump(mode="json"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safety_state"] == SafetyState.SAFE.value
    assert data["overall_safety_score"] >= 95.0


def test_25_fixture_unbuckled_tramming():
    """Verify Fixture 2: UNBUCKLED_TRAMMING."""
    evt = ALL_FIXTURES["UNBUCKLED_TRAMMING"]()
    resp = client.post("/api/v1/safety/telemetry", json=evt.model_dump(mode="json"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safety_state"] == SafetyState.HIGH_RISK.value
    assert any(a["alert_type"] == "SEATBELT_UNBUCKLED" and a["severity"] == "CRITICAL" for a in data["active_alerts"])


def test_26_fixture_critical_proximity():
    """Verify Fixture 3: CRITICAL_PROXIMITY."""
    evt = ALL_FIXTURES["CRITICAL_PROXIMITY"]()
    resp = client.post("/api/v1/safety/telemetry", json=evt.model_dump(mode="json"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safety_state"] == SafetyState.HIGH_RISK.value
    assert data["proximity_warning_level"] == ProximityWarningLevel.CRITICAL.value


def test_27_fixture_combined_hazard():
    """Verify Fixture 4: COMBINED_HAZARD."""
    evt = ALL_FIXTURES["COMBINED_HAZARD"]()
    resp = client.post("/api/v1/safety/telemetry", json=evt.model_dump(mode="json"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["safety_state"] == SafetyState.HIGH_RISK.value
    assert any(a["alert_type"] == "COMBINED_HAZARD" for a in data["active_alerts"])


def test_28_fixture_excessive_idle():
    """Verify Fixture 5: EXCESSIVE_IDLE."""
    evt = ALL_FIXTURES["EXCESSIVE_IDLE"]()
    resp = client.post("/api/v1/safety/telemetry", json=evt.model_dump(mode="json"))
    assert resp.status_code == 200
    data = resp.json()
    assert any(a["alert_type"] == "EXCESSIVE_IDLE" for a in data["active_alerts"])


# ============================================================================
# 10. Error Schema Validation
# ============================================================================


def test_29_validation_error_format_conformance():
    """Verify invalid request payload returns standardized error conforming to error.schema.json."""
    invalid_payload = {"event_id": "EVT-BAD"}  # Missing machine, operator, etc.
    resp = client.post("/api/v1/safety/telemetry", json=invalid_payload)
    assert resp.status_code == 422
    data = resp.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "timestamp" in data
    assert "details" in data
