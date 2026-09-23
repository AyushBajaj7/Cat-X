"""FastAPI routes for API Gateway (Port 8080)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
import httpx

from .config import settings
from .clients import clients
from .demo import demo_engine

router = APIRouter(prefix="/api/v1", tags=["gateway"])


@router.get("/health")
async def composite_health():
    """Composite health check querying all downstream microservices."""
    downstream_status = await clients.check_health()
    all_healthy = all(s == "HEALTHY" for s in downstream_status.values())
    return {
        "status": "HEALTHY" if all_healthy else "PARTIAL_DEGRADED",
        "service": "api-gateway",
        "port": settings.service_port,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "downstream": downstream_status,
    }


@router.post("/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def ingest_telemetry_fanout(telemetry: Dict[str, Any]):
    """Unified telemetry ingestion gateway endpoint that fans out to downstream services."""
    res = await clients.forward_telemetry(telemetry)
    return {
        "status": "ACCEPTED",
        "message": "Telemetry event received and forwarded for safety and twin processing.",
        "downstream_ack": res,
    }


@router.get("/dashboard/{operator_id}")
async def get_operator_dashboard(operator_id: str):
    """Aggregate dashboard view composing Shift Twin, Safety Status, and Training Recommendations."""
    twin = await clients.get_shift_twin(operator_id)
    safety = await clients.get_safety_status(operator_id)
    recommendations = await clients.get_training_recommendations(operator_id)
    demo_info = demo_engine.get_current_state()

    return {
        "operator_id": operator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shift_twin_summary": twin,
        "immediate_safety_status": safety,
        "top_training_recommendation": recommendations[0] if recommendations else None,
        "active_alerts_count": safety.get("active_hazard_count", 0),
        "attention_mode": twin.get("attention_mode", demo_info.get("attention_mode", "NORMAL")),
        "attention_reason": twin.get("attention_reason", demo_info.get("attention_reason", "Nominal operating parameters.")),
        "active_decision_point": demo_info.get("decision_point"),
        "trajectory_card": {
            "scenarios_count": len(demo_info.get("scenarios", [])),
            "chosen_scenario": demo_engine.chosen_scenario,
        } if demo_info.get("decision_point") else None,
        "demo_step": demo_engine.current_step,
        "demo_step_name": demo_info.get("step_name"),
    }


@router.get("/shift/{operator_id}")
async def get_operator_shift_twin(operator_id: str):
    """Retrieve full canonical Shift Twin object via Gateway."""
    return await clients.get_shift_twin(operator_id)


# ============================================================
# TASK MANAGEMENT ENDPOINTS (Proxied to Operations Service)
# ============================================================

@router.get("/tasks")
async def list_tasks(status_filter: Optional[str] = Query(default=None, alias="status")):
    """Proxy task list request to the operations service."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            url = f"{settings.operations_service_url}/api/v1/tasks"
            if status_filter:
                url += f"?status={status_filter}"
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    # Fallback default task list when standalone
    return [
        {
            "task_id": "T002",
            "title": "Bench 2 Deep Trenching & Excavation",
            "description": "Excavate 850 tons of sandstone overburden along Bench 2 trench line.",
            "site_zone": "BENCH_2_NORTH",
            "target_volume_tons": 850.0,
            "completed_volume_tons": 320.0,
            "status": "IN_PROGRESS",
            "priority": "CRITICAL",
            "estimated_duration_minutes": 240,
        },
        {
            "task_id": "T003",
            "title": "Bench 3 Overburden Pre-strip",
            "description": "Stockpile soft topsoil to enable rapid truck cycle loading.",
            "site_zone": "BENCH_3_UPPER",
            "target_volume_tons": 450.0,
            "completed_volume_tons": 0.0,
            "status": "PENDING",
            "priority": "NORMAL",
            "estimated_duration_minutes": 120,
        },
    ]


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Proxy a single task lookup."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.get(f"{settings.operations_service_url}/api/v1/tasks/{task_id}")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    tasks = await list_tasks()
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if task:
        return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")


@router.post("/tasks/estimate")
async def estimate_task(payload: Dict[str, Any]):
    """Proxy task estimate request."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.post(f"{settings.operations_service_url}/api/v1/tasks/estimate", json=payload)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return {
        "task_id": payload.get("task_id", "T002"),
        "estimated_remaining_minutes": 145.0,
        "estimated_completion_time": "2026-09-23T14:17:00Z",
        "confidence_score": 0.92,
        "p10_minutes": 138.0,
        "p90_minutes": 162.0,
    }


@router.post("/tasks/what-if")
async def what_if(payload: Dict[str, Any]):
    """Proxy what-if simulation request."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.post(f"{settings.operations_service_url}/api/v1/tasks/what-if", json=payload)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    # Deterministic simulation response for what-if exploration
    idle_red = float(payload.get("simulated_idle_reduction_pct", 15.0) or 15.0)
    time_saved = round(idle_red * 1.15, 1)
    fuel_saved = round(time_saved * 0.95, 1)
    return {
        "task_id": payload.get("task_id", "T002"),
        "simulated_parameters": payload,
        "time_saved_minutes": time_saved,
        "fuel_saved_liters": fuel_saved,
        "predicted_shift_delay_minutes": max(0.0, 17.0 - time_saved),
        "summary": f"Simulating {idle_red}% idle reduction yields {time_saved} minutes saved and {fuel_saved}L fuel saved.",
    }


# ============================================================
# SAFETY SERVICE ENDPOINTS (Proxied to Safety Service)
# ============================================================

@router.get("/safety/status/{operator_id}")
async def get_safety_status(operator_id: str):
    """Proxy safety status."""
    return await clients.get_safety_status(operator_id)


@router.get("/safety/alerts/{operator_id}")
async def get_safety_alerts(operator_id: str, severity: Optional[str] = Query(default=None)):
    """Proxy safety alerts."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            url = f"{settings.safety_service_url}/api/v1/safety/alerts/{operator_id}"
            if severity:
                url += f"?severity={severity}"
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    demo_info = demo_engine.get_current_state()
    alerts = []
    if not demo_info["seatbelt_fastened"]:
        alerts.append({
            "alert_id": "ALT-SEATBELT-01",
            "operator_id": operator_id,
            "timestamp": demo_info["timestamp"],
            "severity": "HIGH",
            "message": "Seatbelt unfastened during machine operation.",
            "acknowledged": False,
        })
    if demo_info["active_hazard_count"] > 0:
        alerts.append({
            "alert_id": "ALT-PROX-01",
            "operator_id": operator_id,
            "timestamp": demo_info["timestamp"],
            "severity": "CRITICAL",
            "message": "Support vehicle inside 14m swing radius exclusion zone.",
            "acknowledged": False,
        })
    return alerts


@router.get("/safety/incidents/{operator_id}")
async def get_safety_incidents(operator_id: str):
    """Proxy safety incidents."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.get(f"{settings.safety_service_url}/api/v1/safety/incidents/{operator_id}")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return []


@router.get("/safety/behaviour/{operator_id}")
async def get_safety_behaviour(operator_id: str):
    """Proxy behaviour state."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.get(f"{settings.safety_service_url}/api/v1/safety/behaviour/{operator_id}")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    demo_info = demo_engine.get_current_state()
    return {
        "operator_id": operator_id,
        "idle_percentage": demo_info["idle_percentage"],
        "behaviour_score": demo_info["behaviour_score"],
        "aggressive_events_count": 0,
        "constraint_flags": {
            "excessive_idling_flag": demo_info["idle_percentage"] > 12.0,
            "speed_limit_flag": False,
            "swing_limit_flag": False,
        },
    }


# ============================================================
# TRAINING SERVICE ENDPOINTS (Proxied to Training Service)
# ============================================================

@router.get("/training/modules")
async def list_training_modules():
    """Expose training modules via the gateway."""
    return await clients.get_training_modules()


@router.get("/training/modules/{module_id}")
async def get_training_module(module_id: str):
    """Expose a specific training module via the gateway."""
    try:
        return await clients.get_training_module(module_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Training module {module_id} not found")


@router.get("/training/recommendations/{operator_id}")
async def get_training_recommendations(operator_id: str, signal: Optional[str] = Query(default=None)):
    """Expose training recommendations via the gateway."""
    return await clients.get_training_recommendations(operator_id, signal=signal)


@router.post("/training/attempts", status_code=status.HTTP_201_CREATED)
async def submit_training_attempt(payload: Dict[str, Any]):
    """Submit a training attempt through the gateway."""
    return await clients.post_training_attempt(payload)


@router.get("/training/progress/{operator_id}")
async def get_training_progress(operator_id: str):
    """Expose training progress via the gateway."""
    return await clients.get_training_progress(operator_id)


# ============================================================
# CAT TRAJECTORY — CONSEQUENCE ENGINE ENDPOINTS
# ============================================================

@router.get("/trajectory/current/{operator_id}")
async def get_current_trajectory_state(operator_id: str):
    """Expose current trajectory state, decision point, and candidate trajectories."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.get(f"{settings.operations_service_url}/api/v1/trajectory/current/{operator_id}")
            if resp.status_code == 200:
                data = resp.json()
                # Attach rich demo consequence and explanation if available
                demo_info = demo_engine.get_current_state()
                if demo_info.get("decision_point"):
                    data["active_decision_point"] = demo_info["decision_point"]
                    data["scenarios"] = demo_info["scenarios"]
                    data["attention_mode"] = demo_info["attention_mode"]
                return data
        except Exception:
            pass

    demo_info = demo_engine.get_current_state()
    dp = demo_info.get("decision_point")
    return {
        "operator_id": operator_id,
        "decision_point_detected": dp is not None,
        "evidence": dp.get("evidence", {}) if dp else {},
        "active_decision_point": dp,
        "available_trajectories": ["SCEN-01-CONTINUE", "SCEN-02-RESEQUENCE", "SCEN-03-REPOSITION"],
        "scenarios": demo_info.get("scenarios", []),
        "attention_mode": demo_info.get("attention_mode", "DECISION_FOCUS"),
        "attention_reason": demo_info.get("attention_reason", "Tactical inflection point detected."),
        "chosen_scenario": demo_engine.chosen_scenario,
        "outcome_replay": demo_info.get("outcome_replay"),
    }


@router.post("/trajectory/detect")
async def detect_decision_point(payload: Dict[str, Any]):
    """Proxy trajectory detection."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.post(f"{settings.operations_service_url}/api/v1/trajectory/detect", json=payload)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    demo_info = demo_engine.get_current_state()
    return demo_info.get("decision_point") or {
        "decision_point_detected": True,
        "decision_point_id": "DP-BENCH2-HAUL-01",
        "trigger_type": "QUEUE_IMBALANCE",
        "severity": "HIGH",
        "summary": "Haul fleet cycle mismatch leading to projected 17-minute delay trap.",
    }


@router.post("/trajectory/evaluate")
async def evaluate_trajectories(payload: Dict[str, Any]):
    """Proxy trajectory evaluation."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.post(f"{settings.operations_service_url}/api/v1/trajectory/evaluate", json=payload)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    demo_info = demo_engine.get_current_state()
    return {
        "decision_point_id": payload.get("decision_point_id", "DP-BENCH2-HAUL-01"),
        "scenarios": demo_info.get("scenarios", []),
    }


@router.post("/trajectory/choose")
async def choose_trajectory(payload: Dict[str, Any]):
    """Proxy trajectory choice and record into demo engine."""
    scenario_id = payload.get("scenario_id", "SCEN-02-RESEQUENCE")
    reason = payload.get("operator_reason", "")
    reason_cat = payload.get("reason_category", "schedule")
    res = demo_engine.record_choice(scenario_id, reason, reason_cat)

    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            await client.post(f"{settings.operations_service_url}/api/v1/trajectory/choose", json=payload)
        except Exception:
            pass

    return res


@router.post("/trajectory/outcome")
async def record_trajectory_outcome(payload: Dict[str, Any]):
    """Proxy outcome recording."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.post(f"{settings.operations_service_url}/api/v1/trajectory/outcome", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                # Ensure required fields are always present
                if "simulated_actual_outcome" not in data or "error_audit" not in data:
                    demo_replay = demo_engine.get_current_state().get("outcome_replay") or _default_outcome_replay()
                    data.setdefault("status", demo_replay["status"])
                    data.setdefault("simulated_actual_outcome", demo_replay.get("simulated_actual_outcome"))
                    data.setdefault("error_audit", demo_replay.get("error_audit"))
                return data
        except Exception:
            pass
    demo_info = demo_engine.get_current_state()
    return demo_info.get("outcome_replay") or _default_outcome_replay()


def _default_outcome_replay() -> Dict[str, Any]:
    """Fallback outcome replay data guaranteeing all required fields are present."""
    return {
        "status": "SIMULATED_COMPLETE",
        "decision_id": f"DEC-{demo_engine.operator_id}-001",
        "chosen_scenario": demo_engine.chosen_scenario or "SCEN-02-RESEQUENCE",
        "predicted_outcome": {
            "eta_minutes": 145.0,
            "fuel_liters": 168.0,
            "idle_minutes": 0.0,
            "shift_delay_minutes": -17.0,
        },
        "simulated_actual_outcome": {
            "eta_minutes": 146.5,
            "fuel_liters": 167.2,
            "idle_minutes": 1.2,
            "shift_delay_minutes": -15.8,
        },
        "prediction_error": {
            "eta_delta_minutes": 1.5,
            "fuel_delta_liters": -0.8,
            "accuracy_pct": 98.9,
        },
        "error_audit": {
            "duration_error_minutes": 1.5,
            "fuel_delta_liters": -0.8,
            "accuracy_pct": 98.9,
        },
        "drift_status": "WITHIN_TOLERANCE",
        "is_simulated": True,
        "simulation_label": "SIMULATED OUTCOME — PROJECTION AUDITED",
    }


@router.get("/trajectory/memory/{operator_id}")
async def get_decision_memory(operator_id: str):
    """Proxy decision memory."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.get(f"{settings.operations_service_url}/api/v1/trajectory/memory/{operator_id}")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return [
        {
            "decision_id": f"DEC-{operator_id}-001",
            "operator_id": operator_id,
            "machine_id": "EXC-CAT-349D",
            "task_id": "T002",
            "timestamp": demo_engine.decision_committed_at or "2026-09-23T10:48:00Z",
            "context_signature": "SIG-BENCH2-WET-TRENCH",
            "context_id": "SIG-BENCH2-WET-TRENCH",
            "available_scenarios": ["SCEN-01-CONTINUE", "SCEN-02-RESEQUENCE", "SCEN-03-REPOSITION"],
            "chosen_scenario": demo_engine.chosen_scenario or "SCEN-02-RESEQUENCE",
            "chosen_scenario_id": demo_engine.chosen_scenario or "SCEN-02-RESEQUENCE",
            "predicted_outcome": {
                "eta_minutes": 145.0,
                "fuel_liters": 168.0,
                "shift_delay_minutes": -17.0,
            },
            "actual_outcome": {
                "eta_minutes": 146.5,
                "fuel_liters": 167.2,
                "shift_delay_minutes": -15.8,
            },
            "actual_result": "15.8 min saved, 15.6L fuel saved, zero deadline delay",
            "prediction_error": {
                "eta_delta_minutes": 1.5,
                "fuel_delta_liters": -0.8,
                "accuracy_pct": 98.9,
            },
            "operator_reason": demo_engine.operator_reason or "Bypassed haul truck queue before rain onset.",
            "source": "OPERATOR_MANUAL_SELECT",
        }
    ]


@router.get("/trajectory/similar/{operator_id}")
async def get_similar_trajectories(operator_id: str):
    """Proxy similar decision context lookups."""
    async with httpx.AsyncClient(timeout=clients.timeout) as client:
        try:
            resp = await client.get(f"{settings.operations_service_url}/api/v1/trajectory/similar/{operator_id}")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    demo_info = demo_engine.get_current_state()
    sim_data = demo_info.get("similar_context") or demo_engine._get_similar_context_data()
    return {
        "operator_id": operator_id,
        "similar_contexts": [sim_data] if sim_data else [],
    }


# ============================================================
# DEMO CONTROLLER ENDPOINTS ("The 17-Minute Trap")
# ============================================================

@router.post("/demo/reset")
async def reset_demo_state():
    """Reset operational and simulation state for deterministic demonstration ('The 17-Minute Trap')."""
    return demo_engine.reset()


@router.get("/demo/state")
async def get_demo_state():
    """Retrieve current state across the 10-step demo lifecycle."""
    return demo_engine.get_current_state()


@router.post("/demo/step")
async def set_demo_step(payload: Optional[Dict[str, Any]] = None):
    """Set or advance demo step."""
    if payload and "step" in payload:
        return demo_engine.set_step(int(payload["step"]))
    return demo_engine.advance_step()
