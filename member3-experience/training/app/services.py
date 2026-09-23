"""Training Service business logic skeleton (Owned by Engineer 3)."""

from datetime import datetime, timezone
from typing import List, Optional
from .models import (
    TrainingAttemptInput,
    TrainingAttemptModel,
    TrainingCategory,
    TrainingDifficulty,
    TrainingModuleModel,
    TrainingProgressModel,
    TrainingRecommendationModel,
    TrainingUrgency,
)


class TrainingService:
    """Core logic layer for training modules, personalized recommendations, and progress tracking."""

    def __init__(self):
        self._modules: dict[str, TrainingModuleModel] = {
            "MOD-SAF-01": TrainingModuleModel(
                module_id="MOD-SAF-01",
                title="Proximity Envelope & Ground Personnel Awareness",
                category=TrainingCategory.SAFETY,
                target_machine_category="EXCAVATOR",
                estimated_duration_minutes=8,
                difficulty=TrainingDifficulty.BEGINNER,
                description="Simulated blind-spot navigation and radar proximity envelope management.",
                learning_objectives=[
                    "Identify blind spots for CAT 349 Excavator",
                    "Establish 3-point radio confirmation before swinging near service trucks",
                ],
                simulator_scenario_id="SIM-BLINDSPOT-01",
            ),
            "MOD-ECO-01": TrainingModuleModel(
                module_id="MOD-ECO-01",
                title="Eco-Mode Power Management & Idle Reduction",
                category=TrainingCategory.ECO_OPERATION,
                target_machine_category="EXCAVATOR",
                estimated_duration_minutes=12,
                difficulty=TrainingDifficulty.INTERMEDIATE,
                description="Techniques to minimize low-idle fuel waste during truck exchange intervals.",
                learning_objectives=[
                    "Utilize automatic engine speed control (AEC)",
                    "Configure auto-idle shutdown threshold to 5 minutes",
                ],
                simulator_scenario_id="SIM-IDLE-02",
            ),
            "MOD-TRENCH-01": TrainingModuleModel(
                module_id="MOD-TRENCH-01",
                title="Precision Trench Grade & Slope Stabilization",
                category=TrainingCategory.MACHINE_HANDLING,
                target_machine_category="EXCAVATOR",
                estimated_duration_minutes=15,
                difficulty=TrainingDifficulty.ADVANCED,
                description="Optimized bucket penetration angle to reduce hydraulic pressure spikes.",
                learning_objectives=[
                    "Maintain continuous bucket curling trajectory",
                    "Avoid high-relief valve pressure during heavy clay excavation",
                ],
                simulator_scenario_id="SIM-TRENCH-03",
            ),
        }

        self._attempts: List[TrainingAttemptModel] = []

    def list_modules(self) -> List[TrainingModuleModel]:
        """List all available training hub modules."""
        return list(self._modules.values())

    def get_module(self, module_id: str) -> Optional[TrainingModuleModel]:
        """Retrieve single training module."""
        return self._modules.get(module_id)

    def get_recommendations(self, operator_id: str) -> List[TrainingRecommendationModel]:
        """Retrieve personalized training recommendations."""
        return [
            TrainingRecommendationModel(
                recommendation_id=f"REC-{operator_id}-01",
                operator_id=operator_id,
                module_id="MOD-ECO-01",
                module_title="Eco-Mode Power Management & Idle Reduction",
                urgency=TrainingUrgency.MEDIUM,
                trigger_source="BEHAVIOUR_ANALYSIS",
                reason="Idling exceeded 12% during Bench 2 haul truck transition phase.",
                recommended_at=datetime.now(timezone.utc),
            )
        ]

    def record_attempt(self, attempt_in: TrainingAttemptInput) -> TrainingAttemptModel:
        """Record simulation or quiz attempt."""
        passed = attempt_in.score_pct >= 80.0
        attempt = TrainingAttemptModel(
            attempt_id=f"ATT-{int(datetime.now(timezone.utc).timestamp())}",
            operator_id=attempt_in.operator_id,
            module_id=attempt_in.module_id,
            score_pct=attempt_in.score_pct,
            passed=passed,
            time_spent_seconds=attempt_in.time_spent_seconds,
            completed_at=datetime.now(timezone.utc),
            feedback="Great work! Focus on engine speed reduction before truck spotting." if passed else "Review AEC activation checklist before retrying.",
        )
        self._attempts.append(attempt)
        return attempt

    def get_progress(self, operator_id: str) -> TrainingProgressModel:
        """Retrieve operator cumulative progress and certifications."""
        operator_attempts = [a for a in self._attempts if a.operator_id == operator_id]
        count = len(operator_attempts)
        avg = (sum(a.score_pct for a in operator_attempts) / count) if count > 0 else 88.5

        return TrainingProgressModel(
            operator_id=operator_id,
            completed_modules_count=max(2, count),
            average_score_pct=avg,
            certifications_earned=["CAT Level 1 Excavator Safety", "Eco-Operator Silver"],
            last_activity_at=datetime.now(timezone.utc),
        )


training_service = TrainingService()
