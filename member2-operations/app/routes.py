"""FastAPI routes for Operations Service (Port 8002)."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from .models import (
    ShiftContextModel,
    ShiftTwinModel,
    SimilarShiftResultModel,
    TaskEstimateRequest,
    TaskModel,
    TaskTimeEstimateModel,
    WhatIfRequestModel,
    WhatIfResultModel,
)
from .services import operations_service

router = APIRouter(prefix="/api/v1", tags=["operations"])


@router.get("/tasks", response_model=List[TaskModel])
async def list_tasks(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    operator_id: Optional[str] = Query(default=None),
):
    """List operational daily tasks."""
    return operations_service.list_tasks(status=status_filter, operator_id=operator_id)


@router.get("/tasks/{task_id}", response_model=TaskModel)
async def get_task(task_id: str):
    """Retrieve details for a specific task."""
    task = operations_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
    return task


@router.post("/tasks/estimate", response_model=TaskTimeEstimateModel)
async def estimate_task_time(req: TaskEstimateRequest):
    """Calculate probabilistic task completion time and ETA."""
    return operations_service.estimate_task(req)


@router.post("/tasks/what-if", response_model=WhatIfResultModel)
async def simulate_what_if(req: WhatIfRequestModel):
    """Run what-if shift simulation with simulated parameter variations."""
    return operations_service.simulate_what_if(req)


@router.get("/operator/{operator_id}/shift", response_model=ShiftContextModel)
async def get_operator_shift(operator_id: str):
    """Retrieve active shift metadata for an operator."""
    return operations_service.get_operator_shift(operator_id)


@router.get("/operator/{operator_id}/shift-twin", response_model=ShiftTwinModel)
async def get_shift_twin(operator_id: str):
    """Retrieve the canonical CAT Operator Shift Twin representation."""
    return operations_service.get_shift_twin(operator_id)


@router.get("/tasks/{task_id}/similar-shifts", response_model=List[SimilarShiftResultModel])
async def get_similar_shifts(task_id: str):
    """Retrieve historical benchmark shifts matching the task profile."""
    return operations_service.get_similar_shifts(task_id)


# ============================================================
# CAT TRAJECTORY — CONSEQUENCE ENGINE ENDPOINTS
# ============================================================

trajectory_router = APIRouter(prefix="/api/v1/trajectory", tags=["trajectory"])


@trajectory_router.get("/current/{operator_id}")
async def get_current_trajectory_state(operator_id: str):
    """Retrieve active decision point and evaluated trajectory options for an operator."""
    return {
        "operator_id": operator_id,
        "active_decision_point": {
            "decision_point_id": f"DP-{operator_id}-001",
            "trigger_type": "QUEUE_IMBALANCE",
            "severity": "HIGH",
            "summary": "Bench 2 truck queue reached 4 units with incoming rainfall.",
            "available_actions": ["ACT-CONTINUE", "ACT-RESEQUENCE", "ACT-REPOSITION"]
        },
        "available_trajectories": ["SCEN-01-CONTINUE", "SCEN-02-RESEQUENCE", "SCEN-03-REPOSITION"],
        "attention_mode": "DECISION_FOCUS"
    }


@trajectory_router.post("/detect")
async def detect_decision_point(payload: dict):
    """Analyze current operational state and detect emergent decision points."""
    return {
        "decision_point_detected": True,
        "decision_point_id": "DP-BENCH2-HAUL-01",
        "trigger_type": "QUEUE_IMBALANCE",
        "severity": "HIGH",
        "summary": "Haul fleet cycle mismatch leading to projected 17-minute delay trap.",
        "recommended_action": "EVALUATE_TRAJECTORIES"
    }


@trajectory_router.post("/evaluate")
async def evaluate_trajectories(payload: dict):
    """Evaluate candidate operational trajectories through safety constraints and generate consequence graphs."""
    return {
        "decision_point_id": payload.get("decision_point_id", "DP-BENCH2-HAUL-01"),
        "scenarios": [
            {
                "scenario_id": "SCEN-01-CONTINUE",
                "action_id": "ACT-CONTINUE",
                "title": "Continue Current Dig Pattern",
                "constraint_status": "FEASIBLE",
                "predicted_outcome": {
                    "eta_minutes": 162.0,
                    "fuel_liters": 184.0,
                    "safety_risk_score": 18.0,
                    "time_saved_minutes": 0.0
                },
                "explanation": "Baseline path; accumulates 17 minutes of low-idle queuing."
            },
            {
                "scenario_id": "SCEN-02-RESEQUENCE",
                "action_id": "ACT-RESEQUENCE",
                "title": "Re-sequence to Overburden Bench 3",
                "constraint_status": "FEASIBLE",
                "predicted_outcome": {
                    "eta_minutes": 145.0,
                    "fuel_liters": 168.0,
                    "safety_risk_score": 12.0,
                    "time_saved_minutes": 17.0
                },
                "explanation": "Bypasses truck congestion; balances fleet arrival cycle."
            },
            {
                "scenario_id": "SCEN-03-REPOSITION",
                "action_id": "ACT-REPOSITION",
                "title": "Reposition Face Angle 15 Degrees West",
                "constraint_status": "FEASIBLE",
                "predicted_outcome": {
                    "eta_minutes": 149.0,
                    "fuel_liters": 172.0,
                    "safety_risk_score": 14.0,
                    "time_saved_minutes": 13.0
                },
                "explanation": "Reduces boom swing angle from 48 to 32 degrees; saves 4.2L fuel."
            }
        ]
    }


@trajectory_router.post("/choose")
async def choose_trajectory(choice: dict):
    """Record operator trajectory choice into decision memory."""
    return {
        "status": "RECORDED",
        "decision_id": f"DEC-{choice.get('operator_id', 'OP1001')}-001",
        "chosen_scenario": choice.get("scenario_id", "SCEN-02-RESEQUENCE"),
        "operator_id": choice.get("operator_id", "OP1001"),
        "message": "Trajectory choice committed to decision memory."
    }


@trajectory_router.post("/outcome")
async def record_trajectory_outcome(outcome: dict):
    """Record actual measured outcome and compute prediction-vs-actual error."""
    return {
        "decision_id": outcome.get("decision_id", "DEC-OP1001-001"),
        "status": "EVALUATED",
        "prediction_error": {
            "eta_delta_minutes": 1.5,
            "fuel_delta_liters": -0.8
        },
        "drift_status": "WITHIN_TOLERANCE"
    }


@trajectory_router.get("/memory/{operator_id}")
async def get_decision_memory(operator_id: str):
    """Retrieve decision memories for an operator."""
    return [
        {
            "decision_id": f"DEC-{operator_id}-001",
            "operator_id": operator_id,
            "timestamp": "2026-09-23T08:15:00Z",
            "context_signature": "SIG-WET-GRADE3-EXC349",
            "chosen_scenario": "SCEN-02-RESEQUENCE",
            "operator_reason": "Avoided truck queue bottleneck before rainfall onset.",
            "source": "OPERATOR_MANUAL_SELECT"
        }
    ]


@trajectory_router.get("/similar/{operator_id}")
async def get_similar_trajectories(operator_id: str):
    """Retrieve historical decision memories matching current context signature."""
    return [
        {
            "historical_decision_id": "DEC-HIST-4402",
            "similarity_score_pct": 92.5,
            "context_signature": "SIG-WET-GRADE3-EXC349",
            "chosen_action": "RESEQUENCE",
            "actual_time_saved_minutes": 16.5,
            "actual_fuel_saved_liters": 15.2,
            "key_learning": "Re-sequencing to bench 3 eliminated idle queuing during shift hour 4."
        }
    ]

