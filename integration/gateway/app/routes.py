"""FastAPI routes for API Gateway (Port 8000)."""

from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, status
from .clients import clients

router = APIRouter(prefix="/api/v1", tags=["gateway"])


@router.get("/health")
async def composite_health():
    """Composite health check querying all downstream microservices."""
    downstream_status = await clients.check_health()
    all_healthy = all(s == "HEALTHY" for s in downstream_status.values())
    return {
        "status": "HEALTHY" if all_healthy else "PARTIAL_DEGRADED",
        "service": "api-gateway",
        "port": 8000,
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

    return {
        "operator_id": operator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shift_twin_summary": twin,
        "immediate_safety_status": safety,
        "top_training_recommendation": recommendations[0] if recommendations else None,
        "active_alerts_count": safety.get("active_hazard_count", 0),
    }


@router.get("/shift/{operator_id}")
async def get_operator_shift_twin(operator_id: str):
    """Retrieve full canonical Shift Twin object via Gateway."""
    return await clients.get_shift_twin(operator_id)
