"""FastAPI route definitions for Safety Service (Port 8001)."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from .models import (
    BehaviourAnalysisModel,
    ConstraintSignal,
    IncidentAcknowledgeRequest,
    IncidentModel,
    IncidentResolveRequest,
    SafetyAlertModel,
    SafetyStatusModel,
    TelemetryEventInput,
)
from .services import safety_service

router = APIRouter(prefix="/api/v1/safety", tags=["safety"])


@router.post(
    "/telemetry",
    response_model=SafetyStatusModel,
    status_code=status.HTTP_200_OK,
    summary="Ingest Telemetry and Evaluate Safety",
    description="Ingest continuous machine/operator telemetry, evaluate hazard rules, log incidents, emit constraints, and return updated safety status.",
)
async def ingest_telemetry(event: TelemetryEventInput) -> SafetyStatusModel:
    """Ingest real-time machine & operator telemetry for immediate safety scoring."""
    return safety_service.process_telemetry(event)


@router.get(
    "/status/{operator_id}",
    response_model=SafetyStatusModel,
    summary="Get Operator Safety Status",
    description="Retrieve real-time safety compliance, proximity level, active hazards, and deterministic safety state for an operator.",
)
async def get_safety_status(operator_id: str) -> SafetyStatusModel:
    """Retrieve current safety compliance and hazard status for an operator."""
    return safety_service.get_status(operator_id)


@router.get(
    "/alerts/{operator_id}",
    response_model=List[SafetyAlertModel],
    summary="List Safety Alerts",
    description="Retrieve active and recent safety alerts for an operator, with optional severity filter.",
)
async def get_safety_alerts(
    operator_id: str,
    severity: Optional[str] = Query(
        default=None,
        description="Filter by alert severity (LOW, MEDIUM, HIGH, CRITICAL)",
    ),
) -> List[SafetyAlertModel]:
    """Retrieve active and recent safety alerts for an operator."""
    return safety_service.get_alerts(operator_id, severity)


@router.get(
    "/incidents/{operator_id}",
    response_model=List[IncidentModel],
    summary="List Safety Incidents",
    description="Retrieve audit incident logs for an operator with optional status filter.",
)
async def get_safety_incidents(
    operator_id: str,
    incident_status: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filter by incident lifecycle status (OPEN, ACKNOWLEDGED, RESOLVED)",
    ),
) -> List[IncidentModel]:
    """Retrieve audit incident logs for an operator."""
    return safety_service.get_incidents(operator_id, incident_status)


@router.post(
    "/incidents/{incident_id}/acknowledge",
    response_model=IncidentModel,
    summary="Acknowledge Safety Incident",
    description="Transition an incident from OPEN to ACKNOWLEDGED.",
)
async def acknowledge_incident(
    incident_id: str,
    request: IncidentAcknowledgeRequest = IncidentAcknowledgeRequest(),
) -> IncidentModel:
    """Acknowledge an open safety incident."""
    incident = safety_service.acknowledge_incident(
        incident_id=incident_id,
        acknowledged_by=request.acknowledged_by,
    )
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found.",
        )
    return incident


@router.post(
    "/incidents/{incident_id}/resolve",
    response_model=IncidentModel,
    summary="Resolve Safety Incident",
    description="Transition an incident to RESOLVED with supervisor notes.",
)
async def resolve_incident(
    incident_id: str,
    request: IncidentResolveRequest,
) -> IncidentModel:
    """Resolve an incident with recorded notes."""
    incident = safety_service.resolve_incident(
        incident_id=incident_id,
        resolved_by=request.resolved_by,
        resolution_notes=request.resolution_notes,
    )
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found.",
        )
    return incident


@router.get(
    "/behaviour/{operator_id}",
    response_model=BehaviourAnalysisModel,
    summary="Get Behaviour Analysis",
    description="Retrieve operator behavioral scores, idle metrics, anomaly detection, and trajectory constraint flags.",
)
async def get_behaviour_analysis(operator_id: str) -> BehaviourAnalysisModel:
    """Retrieve operator behavior score, idle metrics, and maneuver flags."""
    return safety_service.get_behaviour_analysis(operator_id)


@router.get(
    "/constraints/{operator_id}",
    response_model=List[ConstraintSignal],
    summary="Get Active Trajectory Constraints",
    description="Retrieve active physical and operational constraint signals for CAT Trajectory engine.",
)
async def get_active_constraints(operator_id: str) -> List[ConstraintSignal]:
    """Retrieve active trajectory constraint signals emitted for an operator."""
    status_obj = safety_service.get_status(operator_id)
    return status_obj.active_constraints


@router.get(
    "/voice-briefing/{operator_id}",
    summary="Get Spoken Safety Briefing",
    description="Generate a natural-language radio dispatch safety briefing for the in-cab audio assistant.",
)
async def get_safety_voice_briefing(operator_id: str) -> dict:
    """Generate concise spoken radio briefing of current safety conditions."""
    status_obj = safety_service.get_status(operator_id)
    if not status_obj.seatbelt_fastened:
        return {
            "operator_id": operator_id,
            "status": "UNSAFE",
            "spoken_briefing": "Critical Safety Alert: Seatbelt unbuckled. Hydraulic lockout armed. Fasten harness before operating implements.",
            "audio_priority": "CRITICAL",
        }
    if status_obj.active_hazard_count > 0:
        return {
            "operator_id": operator_id,
            "status": "WARNING",
            "spoken_briefing": f"Proximity Warning: {status_obj.active_hazard_count} active hazard detected in your 15-meter counterweight swing zone. Halt boom slew immediately.",
            "audio_priority": "HIGH",
        }
    return {
        "operator_id": operator_id,
        "status": "SAFE",
        "spoken_briefing": f"Cab safety perimeter is 100% clear. Zero proximity hazards. Harness latched with {status_obj.seatbelt_compliance_pct}% compliance streak. Highwall geotechnical slope is stable.",
        "audio_priority": "NORMAL",
    }

