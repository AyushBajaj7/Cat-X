"""FastAPI routes for Safety Service (Port 8001)."""

from typing import List, Optional
from fastapi import APIRouter, Query, status
from .models import (
    BehaviourAnalysisModel,
    IncidentModel,
    SafetyAlertModel,
    SafetyStatusModel,
    TelemetryEventInput,
)
from .services import safety_service

router = APIRouter(prefix="/api/v1/safety", tags=["safety"])


@router.post("/telemetry", response_model=SafetyStatusModel, status_code=status.HTTP_200_OK)
async def ingest_telemetry(event: TelemetryEventInput):
    """Ingest real-time telemetry and return immediate safety status."""
    return safety_service.process_telemetry(event)


@router.get("/status/{operator_id}", response_model=SafetyStatusModel)
async def get_safety_status(operator_id: str):
    """Retrieve current safety compliance and hazard status for an operator."""
    return safety_service.get_status(operator_id)


@router.get("/alerts/{operator_id}", response_model=List[SafetyAlertModel])
async def get_safety_alerts(
    operator_id: str,
    severity: Optional[str] = Query(default=None, description="Filter by alert severity")
):
    """Retrieve active and recent safety alerts for an operator."""
    return safety_service.get_alerts(operator_id, severity)


@router.get("/incidents/{operator_id}", response_model=List[IncidentModel])
async def get_safety_incidents(operator_id: str):
    """Retrieve audit incident logs for an operator."""
    return safety_service.get_incidents(operator_id)


@router.get("/behaviour/{operator_id}", response_model=BehaviourAnalysisModel)
async def get_behaviour_analysis(operator_id: str):
    """Retrieve operator behavior score, idle metrics, and maneuver flags."""
    return safety_service.get_behaviour_analysis(operator_id)
