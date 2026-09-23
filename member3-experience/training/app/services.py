"""Training Service business logic for the CAT Operator Shift Twin."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from .models import (
    ScenarioChoice,
    ScenarioStep,
    TrainingAttemptInput,
    TrainingAttemptModel,
    TrainingCategory,
    TrainingModuleModel,
    TrainingProgressModel,
    TrainingRecommendationModel,
    TrainingUrgency,
)


LEGACY_MODULE_ALIASES = {
    "MOD-SAF-01": "SAFE_START_01",
    "MOD-PROX-01": "PROXIMITY_RESPONSE_01",
    "MOD-IDLE-01": "IDLE_EFFICIENCY_01",
    "MOD-DECISION-01": "DECISION_AWARENESS_01",
}


class TrainingService:
    """Core logic layer for training modules, recommendations, and progress tracking."""

    def __init__(self):
        self._modules: dict[str, TrainingModuleModel] = {
            "SAFE_START_01": TrainingModuleModel(
                module_id="SAFE_START_01",
                title="Safe Start Check",
                description="Identify startup conditions, confirm the operator environment, and complete a safe start before work begins.",
                objective="Confirm a safe operating context before beginning the task.",
                difficulty="BEGINNER",
                estimated_minutes=8,
                skills=["safety checks", "seatbelt compliance", "site awareness"],
                steps=[
                    "Identify startup conditions.",
                    "Confirm safety context.",
                    "Confirm seatbelt is secure.",
                    "Check operating environment.",
                    "Make the safe decision before moving."
                ],
                scenario_steps=[
                    ScenarioStep(
                        step_number=1,
                        title="Identify Startup Conditions",
                        prompt="Before switching the battery disconnect and turning ignition, what is the required first action?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Complete 360-degree walkaround inspection, fluid checks, and ground stance validation.", is_correct=True, explanation="Standard Caterpillar pre-operation procedure."),
                            ScenarioChoice(choice_id="C2", text="Turn ignition immediately to warm engine hydraulics.", is_correct=False, explanation="Never ignite without physical walkaround inspection."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=2,
                        title="Confirm Safety Context",
                        prompt="Where must the machine be stationed during initial pre-shift startup?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Parked on firm, level ground with bucket lowered and hydraulic lockout lever engaged.", is_correct=True, explanation="Prevents unintended hydraulic articulation."),
                            ScenarioChoice(choice_id="C2", text="Stationed on a 15-degree haul slope with attachments hovering.", is_correct=False, explanation="Unstable slope stance introduces roll hazard."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=3,
                        title="Confirm Seatbelt Compliance",
                        prompt="The cab safety interlock detects an unbuckled harness. What action is required?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Fasten the 3-point seatbelt firmly and confirm the cab safety beacon switches green.", is_correct=True, explanation="Seatbelt compliance is mandatory prior to hydraulic arming."),
                            ScenarioChoice(choice_id="C2", text="Rev engine throttle to override the seatbelt buzzer.", is_correct=False, explanation="Overriding safety sensors violates site rules."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=4,
                        title="Check Operating Environment",
                        prompt="Before lifting the work tool, what perimeter verification is mandatory?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Scan mirror/camera blindspots and verify no personnel or support vehicles within swing radius.", is_correct=True, explanation="Guarantees safe clearance before swing."),
                            ScenarioChoice(choice_id="C2", text="Assume nearby personnel will stay clear once the engine hums.", is_correct=False, explanation="Assumption causes swing collisions."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=5,
                        title="Make Safe Decision",
                        prompt="All checks pass. What is the final action before swinging the boom?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Sound two horn blasts, release hydraulic lockout, and verify control responsiveness.", is_correct=True, explanation="Signals surrounding personnel before machine motion."),
                            ScenarioChoice(choice_id="C2", text="Slew immediately at maximum RPM.", is_correct=False, explanation="Aggressive swing risks sudden load shift."),
                        ]
                    ),
                ],
                category=TrainingCategory.SAFETY,
            ),
            "PROXIMITY_RESPONSE_01": TrainingModuleModel(
                module_id="PROXIMITY_RESPONSE_01",
                title="Proximity Response",
                description="Respond to a nearby hazard by recognizing the risk and choosing the safest operational response.",
                objective="Identify a proximity hazard and choose the correct response.",
                difficulty="INTERMEDIATE",
                estimated_minutes=10,
                skills=["hazard recognition", "situational awareness", "decision-making"],
                steps=[
                    "Identify the hazard.",
                    "Assess the changing situation.",
                    "Choose an appropriate response.",
                    "Confirm the safe operating path."
                ],
                scenario_steps=[
                    ScenarioStep(
                        step_number=1,
                        title="Identify Hazard",
                        prompt="Proximity sensor flashes AMBER: a support vehicle enters the 14m swing perimeter. What is the hazard?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Light utility vehicle inside the machine's dynamic tail-swing boundary.", is_correct=True, explanation="Proximity breach creates immediate crush/collision hazard."),
                            ScenarioChoice(choice_id="C2", text="Routine bench activity; continue bucket cycling.", is_correct=False, explanation="Ignoring sensor triggers safety incident."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=2,
                        title="Assess Situation",
                        prompt="The utility vehicle is traveling along the blind counterweight path. How do you assess the risk?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="High risk: vehicle is in operator blind spot during rapid slew cycle.", is_correct=True, explanation="Accurate blind spot risk assessment."),
                            ScenarioChoice(choice_id="C2", text="Low risk: counterweight will clear vehicle roof.", is_correct=False, explanation="Severe safety misjudgment."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=3,
                        title="Choose Appropriate Response",
                        prompt="What is the required immediate operational response?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Halt swing immediately, lower bucket to ground, sound horn, and establish radio contact.", is_correct=True, explanation="Immediate safe stop neutralizes kinetic energy."),
                            ScenarioChoice(choice_id="C2", text="Accelerate swing to complete current truck load pass.", is_correct=False, explanation="Increases collision probability."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=4,
                        title="Confirm Safe Operating Path",
                        prompt="The utility truck retreats past the 20m safety zone. When is it safe to resume?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Confirm proximity alarm clears, re-check mirrors, and resume at controlled swing speed.", is_correct=True, explanation="Verified clearance before resumption."),
                            ScenarioChoice(choice_id="C2", text="Swing rapidly without visual check.", is_correct=False, explanation="Second hazard could be present."),
                        ]
                    ),
                ],
                category=TrainingCategory.SAFETY,
            ),
            "IDLE_EFFICIENCY_01": TrainingModuleModel(
                module_id="IDLE_EFFICIENCY_01",
                title="Idle Efficiency Response",
                description="Recognize inefficient idle and apply the correct operational action to reduce wasted energy and delay.",
                objective="Reduce inefficient idle and restore productive operation.",
                difficulty="INTERMEDIATE",
                estimated_minutes=12,
                skills=["fuel management", "idle reduction", "operational flow"],
                steps=[
                    "Identify the inefficient idle condition.",
                    "Choose the appropriate operational response.",
                    "Reduce wasted time and fuel.",
                    "Resume productive workflow."
                ],
                scenario_steps=[
                    ScenarioStep(
                        step_number=1,
                        title="Identify Inefficient Idle",
                        prompt="Haul trucks are bunched at the crusher for 18 minutes. Engine is running at 1800 RPM. What is the impact?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="18.5 L/hr fuel burn with zero tons moved, accelerating unnecessary machine hour meter accumulation.", is_correct=True, explanation="Identifies low-idle efficiency trap."),
                            ScenarioChoice(choice_id="C2", text="Normal engine standby with no cost impact.", is_correct=False, explanation="High idle burns significant fuel unproductively."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=2,
                        title="Choose Operational Response",
                        prompt="What operational response restores efficiency during the truck gap?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Engage Auto-Engine Control (AEC) or re-sequence to pre-strip bench overburden.", is_correct=True, explanation="Turns dead idle into productive soil preparation."),
                            ScenarioChoice(choice_id="C2", text="Keep engine revved to keep hydraulic oil heated.", is_correct=False, explanation="Wastes fuel without necessity."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=3,
                        title="Reduce Wasted Time and Fuel",
                        prompt="By pre-stripping 180 tons of overburden during the truck delay, what consequence occurs?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Soil is loosened in advance, reducing subsequent truck load time by 35 seconds per truck.", is_correct=True, explanation="Consequence of tactical re-sequencing."),
                            ScenarioChoice(choice_id="C2", text="Machine fuel efficiency drops.", is_correct=False, explanation="Productive load improves efficiency ratio."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=4,
                        title="Resume Productive Workflow",
                        prompt="The 4-truck platoon arrives. How does the operator capitalize on the re-sequenced bench?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Direct load the pre-loosened stock at maximum fill factor, clearing the queue with minimal truck wait.", is_correct=True, explanation="Restores peak fleet cycle flow."),
                            ScenarioChoice(choice_id="C2", text="Tell trucks to wait while taking a break.", is_correct=False, explanation="Compounds haul fleet delays."),
                        ]
                    ),
                ],
                category=TrainingCategory.ECO_OPERATION,
            ),
            "DECISION_AWARENESS_01": TrainingModuleModel(
                module_id="DECISION_AWARENESS_01",
                title="Decision Awareness",
                description="Review a simplified machine decision, compare alternatives, and understand the consequence of each operational choice.",
                objective="Understand the link between operator decisions and operational consequences.",
                difficulty="ADVANCED",
                estimated_minutes=14,
                skills=["trajectory comparison", "consequence reading", "decision trace"],
                steps=[
                    "Present a simplified operational decision.",
                    "Show trajectories or alternatives.",
                    "Ask the operator to select a path.",
                    "Show expected consequences.",
                    "Connect the decision to the shift outcome."
                ],
                scenario_steps=[
                    ScenarioStep(
                        step_number=1,
                        title="Present Operational Decision",
                        prompt="CAT Trajectory flags a Decision Point: 18-minute truck gap and approaching rain front. What is at stake?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Compounding truck delay and wet ground will lock the excavator in a 17-minute completion delay.", is_correct=True, explanation="Identifies the 17-minute trap."),
                            ScenarioChoice(choice_id="C2", text="Nothing; shift output will automatically balance.", is_correct=False, explanation="Passive stance leads to deadline failure."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=2,
                        title="Show Trajectory Alternatives",
                        prompt="Three candidate paths are generated: Continue (A), Resequence (B), Reposition (C). How are they evaluated?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Through safety constraints, ETA forecasting, fuel proxy, and idle impact.", is_correct=True, explanation="Multi-dimensional consequence evaluation."),
                            ScenarioChoice(choice_id="C2", text="Through arbitrary random ranking.", is_correct=False, explanation="Trajectories are systematically modeled."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=3,
                        title="Select Tactical Trajectory",
                        prompt="Operator selects Trajectory B: Resequence to Upper Bench 3. Why is this superior to Continue?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Eliminates idle delay, completes trench 12 min early, and saves 14.8L fuel before rain.", is_correct=True, explanation="Tactical optimization of shift outcome."),
                            ScenarioChoice(choice_id="C2", text="It is the only path that uses maximum engine power.", is_correct=False, explanation="Selection is based on composite shift value."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=4,
                        title="Show Consequence Chain",
                        prompt="What does the Consequence Graph reveal about this human decision?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Causal chain: Resequence Choice -> Zero Idle -> High Fill Factor -> Fast Loading -> On-Time Finish.", is_correct=True, explanation="Visualizes multi-order causal propagation."),
                            ScenarioChoice(choice_id="C2", text="A disconnected list of machine errors.", is_correct=False, explanation="Consequence graphs represent causal flows."),
                        ]
                    ),
                    ScenarioStep(
                        step_number=5,
                        title="Connect to Shift Outcome & Decision Memory",
                        prompt="What happens after the operator executes this trajectory choice?",
                        choices=[
                            ScenarioChoice(choice_id="C1", text="Choice and outcome are recorded in Decision Memory, available for similar future shift contexts.", is_correct=True, explanation="Closes the adaptive learning loop."),
                            ScenarioChoice(choice_id="C2", text="The decision data is discarded immediately.", is_correct=False, explanation="Decision memory builds organizational intelligence."),
                        ]
                    ),
                ],
                category=TrainingCategory.MACHINE_HANDLING,
            ),
        }

        self._attempts: List[TrainingAttemptModel] = []

    def list_modules(self) -> List[TrainingModuleModel]:
        """List all available training modules."""
        return list(self._modules.values())

    def get_module(self, module_id: str) -> Optional[TrainingModuleModel]:
        """Retrieve a particular training module, supporting legacy aliases."""
        resolved_id = LEGACY_MODULE_ALIASES.get(module_id, module_id)
        module = self._modules.get(resolved_id)
        if module is None:
            return None
        if module_id in LEGACY_MODULE_ALIASES:
            return module.model_copy(update={"module_id": module_id})
        return module

    def get_recommendations(self, operator_id: str, signal: Optional[str] = None) -> List[TrainingRecommendationModel]:
        """Return personalized training recommendations based on contextual operational signals."""
        signal_map = [
            ("seatbelt violation", "SAFE_START_01", "Safe Start Check", "Seatbelt non-compliance detected. Review safe operating procedures and startup sequence before continuing."),
            ("proximity event", "PROXIMITY_RESPONSE_01", "Proximity Response", "Proximity boundary alert triggered. Review site hazard identification and response guidelines."),
            ("high idle", "IDLE_EFFICIENCY_01", "Idle Efficiency Response", "Excessive low-idle operation observed. Review engine power management and queue mitigation techniques."),
            ("decision-related pattern", "DECISION_AWARENESS_01", "Decision Awareness", "Emergent tactical decision point encountered. Review consequence graphs and trajectory trade-offs."),
        ]

        recs: List[TrainingRecommendationModel] = []
        for sig_name, module_id, title, reason in signal_map:
            if signal and signal.lower() not in sig_name.lower():
                continue
            recs.append(
                TrainingRecommendationModel(
                    recommendation_id=f"REC-{operator_id}-{module_id}",
                    operator_id=operator_id,
                    module_id=module_id,
                    module_title=title,
                    urgency=TrainingUrgency.MEDIUM,
                    trigger_source="CONTEXT_SIGNAL",
                    reason=reason,
                    signal=sig_name,
                    value="detected",
                )
            )
        return recs

    def record_attempt(self, attempt_in: TrainingAttemptInput) -> TrainingAttemptModel:
        """Record a deterministic training attempt with score and percentage."""
        started_at = attempt_in.started_at or datetime.now(timezone.utc)
        completed_at = attempt_in.completed_at or datetime.now(timezone.utc)
        normalized_module_id = LEGACY_MODULE_ALIASES.get(attempt_in.module_id, attempt_in.module_id)
        max_score = attempt_in.max_score or 100.0
        score_value = attempt_in.score if attempt_in.score is not None else (attempt_in.score_pct or 0.0)
        percentage = round((score_value / max_score) * 100.0, 2) if max_score else 0.0
        passed = percentage >= 80.0
        attempt = TrainingAttemptModel(
            attempt_id=f"ATT-{uuid4().hex[:12].upper()}",
            operator_id=attempt_in.operator_id,
            module_id=normalized_module_id,
            started_at=started_at,
            completed_at=completed_at,
            score=score_value,
            max_score=max_score,
            percentage=percentage,
            mistakes=attempt_in.mistakes,
            passed=passed,
            status=attempt_in.status or "COMPLETED",
            score_pct=score_value,
            time_spent_seconds=attempt_in.time_spent_seconds or 0,
            feedback=attempt_in.feedback,
        )
        self._attempts.append(attempt)
        return attempt

    def get_progress(self, operator_id: str) -> TrainingProgressModel:
        """Retrieve the cumulative operator training progress."""
        operator_attempts = [a for a in self._attempts if a.operator_id == operator_id]
        completed_modules_count = len({a.module_id for a in operator_attempts}) if operator_attempts else 0
        avg_percentage = round(sum(a.percentage for a in operator_attempts) / len(operator_attempts), 2) if operator_attempts else 0.0

        return TrainingProgressModel(
            operator_id=operator_id,
            completed_modules_count=max(1, completed_modules_count) if operator_attempts else 0,
            average_score_pct=avg_percentage,
            certifications_earned=["CAT Level 1 Safety Basics", "Decision Awareness Fundamentals"],
            last_activity_at=max((a.completed_at for a in operator_attempts), default=datetime.now(timezone.utc)),
        )


training_service = TrainingService()
