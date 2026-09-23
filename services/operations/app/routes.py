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
