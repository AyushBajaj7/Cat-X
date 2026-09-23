"""FastAPI routes for Training Service (Port 8003)."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from .models import (
    TrainingAttemptInput,
    TrainingAttemptModel,
    TrainingModuleModel,
    TrainingProgressModel,
    TrainingRecommendationModel,
)
from .services import training_service

router = APIRouter(prefix="/api/v1/training", tags=["training"])


@router.get("/modules", response_model=List[TrainingModuleModel])
async def list_modules():
    """List available training hub modules."""
    return training_service.list_modules()


@router.get("/modules/{module_id}", response_model=TrainingModuleModel)
async def get_module(module_id: str):
    """Retrieve syllabus and simulator configuration for a training module."""
    module = training_service.get_module(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training module {module_id} not found."
        )
    return module


@router.get("/recommendations/{operator_id}", response_model=List[TrainingRecommendationModel])
async def get_recommendations(operator_id: str, signal: Optional[str] = None):
    """Retrieve personalized training recommendations for an operator."""
    return training_service.get_recommendations(operator_id, signal=signal)


@router.post("/attempts", response_model=TrainingAttemptModel, status_code=status.HTTP_201_CREATED)
async def record_attempt(attempt: TrainingAttemptInput):
    """Record completion of a training scenario or quiz."""
    return training_service.record_attempt(attempt)


@router.get("/progress/{operator_id}", response_model=TrainingProgressModel)
async def get_progress(operator_id: str):
    """Retrieve training completion status and certifications for an operator."""
    return training_service.get_progress(operator_id)
