"""
FastAPI Routes for Operations Service (Port 8002).
Implements all 14 required endpoints conforming strictly to /shared/contracts/.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
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
    """List operational daily assignments for earthmoving operations."""
    return operations_service.list_tasks(status=status_filter, operator_id=operator_id)


@router.get("/tasks/{task_id}", response_model=TaskModel)
async def get_task(task_id: str):
    """Retrieve detailed specifications of a specific task."""
    task = operations_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": f"Task with ID {task_id} not found.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    return task


@router.post("/tasks/estimate", response_model=TaskTimeEstimateModel)
async def estimate_task_time(req: TaskEstimateRequest):
    """Calculate probabilistic task completion time and ETA."""
    try:
        return operations_service.estimate_task(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "VALIDATION_ERROR",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


@router.post("/tasks/what-if", response_model=WhatIfResultModel)
async def simulate_what_if(req: WhatIfRequestModel):
    """Run what-if shift simulation evaluating how parameter shifts alter outcome."""
    try:
        return operations_service.simulate_what_if(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "VALIDATION_ERROR",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


@router.get("/operator/{operator_id}/shift", response_model=ShiftContextModel)
async def get_operator_shift(operator_id: str):
    """Retrieve current shift context, status, and active task assignment."""
    return operations_service.get_operator_shift(operator_id)


@router.get("/operator/{operator_id}/shift-twin", response_model=ShiftTwinModel)
async def get_shift_twin(operator_id: str):
    """Retrieve the canonical 7-dimension Shift Twin representation."""
    return operations_service.get_shift_twin(operator_id)


@router.get("/tasks/{task_id}/similar-shifts", response_model=List[SimilarShiftResultModel])
async def get_similar_shifts(task_id: str):
    """Query historical completed shifts matching the task profile."""
    return operations_service.get_similar_shifts(task_id)


# ============================================================
# CAT TRAJECTORY — CONSEQUENCE ENGINE ENDPOINTS
# ============================================================

trajectory_router = APIRouter(prefix="/api/v1/trajectory", tags=["trajectory"])


@trajectory_router.get("/current/{operator_id}")
async def get_current_trajectory_state(operator_id: str):
    """Retrieve active decision point and candidate trajectories for an operator."""
    return operations_service.get_current_trajectory(operator_id)


@trajectory_router.post("/detect")
async def detect_decision_point(payload: Dict[str, Any]):
    """Evaluate incoming operational signals to detect emergent decision points."""
    return operations_service.detect_decision_point(payload)


@trajectory_router.post("/evaluate")
async def evaluate_trajectories(payload: Dict[str, Any]):
    """Evaluate candidate operational trajectories against safety constraints and generate consequence graphs."""
    return operations_service.evaluate_trajectories(payload)


@trajectory_router.post("/choose")
async def choose_trajectory(choice: Dict[str, Any]):
    """Record operator trajectory selection into active operational state and decision memory."""
    if not choice.get("scenario_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "VALIDATION_ERROR",
                "message": "scenario_id is required.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    return operations_service.choose_trajectory(choice)


@trajectory_router.post("/outcome")
async def record_trajectory_outcome(outcome: Dict[str, Any]):
    """Record actual measured outcome after trajectory execution and compute prediction error."""
    try:
        return operations_service.record_outcome(outcome)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


@trajectory_router.get("/memory/{operator_id}")
async def get_decision_memory(operator_id: str):
    """Retrieve historical decision memories recorded for this operator."""
    return operations_service.get_decision_memories(operator_id)


@trajectory_router.get("/similar/{operator_id}")
async def get_similar_trajectories(operator_id: str):
    """Retrieve historical decision memories matching current operational context signature."""
    return operations_service.get_similar_trajectories(operator_id)
