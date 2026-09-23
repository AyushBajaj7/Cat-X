"""
CAT Trajectory — Scenario Generator.
Generates candidate alternative operational trajectories (Continue, Resequence, Reposition)
by applying transparent parameter transformations to cloned operational states.
Conforms strictly to shared/contracts/scenario.schema.json.
"""

import copy
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from ..domain.operational_state import OperationalState


class ScenarioStrategyConfig(BaseModel):
    """Configuration parameters for candidate trajectory transformation."""
    action_id: str
    title: str
    description: str
    queue_multiplier: float
    idle_multiplier: float
    cycle_time_multiplier: float
    swing_angle_target_deg: float
    transition_time_minutes: float
    slope_modifier_deg: float = 0.0
    hazard_risk_modifier: float = 0.0
    explanation_template: str


# Standard archetype configurations for earthmoving operations
DEFAULT_STRATEGIES: Dict[str, ScenarioStrategyConfig] = {
    "ACT-CONTINUE": ScenarioStrategyConfig(
        action_id="ACT-CONTINUE",
        title="Continue Current Dig Pattern",
        description="Maintain current bench stance and await queued haul fleet cycle.",
        queue_multiplier=1.00,
        idle_multiplier=1.28,
        cycle_time_multiplier=1.06,
        swing_angle_target_deg=48.0,
        transition_time_minutes=0.0,
        slope_modifier_deg=0.0,
        hazard_risk_modifier=0.0,
        explanation_template="Baseline path: excavator idles at high RPM awaiting haul platoon; compounding rain increases delay.",
    ),
    "ACT-RESEQUENCE": ScenarioStrategyConfig(
        action_id="ACT-RESEQUENCE",
        title="Re-sequence to Overburden Bench 3",
        description="Pivot immediately to pre-strip 180 tons of soft overburden from Upper Bench 3 while truck fleet clears bottleneck.",
        queue_multiplier=0.20,
        idle_multiplier=0.12,
        cycle_time_multiplier=0.88,
        swing_angle_target_deg=42.0,
        transition_time_minutes=2.0,
        slope_modifier_deg=1.0,  # Bench 3 slope is 8.5 deg (safe)
        hazard_risk_modifier=-5.0,
        explanation_template="Tactical pivot: converts 18 minutes of idle waiting into productive pre-stripping; absorbs truck platoon smoothly.",
    ),
    "ACT-REPOSITION": ScenarioStrategyConfig(
        action_id="ACT-REPOSITION",
        title="Reposition Face Angle 15 Degrees West",
        description="Walk machine 12 meters along bench to realign digging face 15° West and re-cone truck spot to cut swing arc from 48° to 32°.",
        queue_multiplier=0.65,
        idle_multiplier=0.35,
        cycle_time_multiplier=0.79,
        swing_angle_target_deg=32.0,
        transition_time_minutes=4.0,
        slope_modifier_deg=-0.5,
        hazard_risk_modifier=-3.0,
        explanation_template="Geometric optimization: reduces slew angle from 48° to 32°, shaving ~6s per bucket cycle and reducing hydraulic heat.",
    ),
}


class CandidateScenario(BaseModel):
    """Container holding scenario metadata and transformed operational state."""
    scenario_id: str
    action_id: str
    title: str
    description: str
    parameters: Dict[str, Any]
    transformed_state: OperationalState
    explanation: str


class TrajectoryScenarioGenerator:
    """Generates candidate operational trajectories from active operational state."""

    def __init__(self, strategies: Optional[Dict[str, ScenarioStrategyConfig]] = None):
        self.strategies = strategies or DEFAULT_STRATEGIES

    def generate_scenarios(
        self,
        current_state: OperationalState,
        action_ids: Optional[List[str]] = None
    ) -> List[CandidateScenario]:
        """Generates transformed candidate scenarios from current state."""
        actions_to_generate = action_ids or list(self.strategies.keys())
        scenarios: List[CandidateScenario] = []

        counter = 1
        for act_id in actions_to_generate:
            strat = self.strategies.get(act_id)
            if not strat:
                continue

            scenario_id = f"SCEN-{counter:02d}-{act_id.replace('ACT-', '')}"
            counter += 1

            # Clone operational state deeply to avoid side-effects
            state_copy = copy.deepcopy(current_state)

            # Apply transparent transformations to the cloned state
            state_copy.queue_state.queue_length = max(
                0, int(round(state_copy.queue_state.queue_length * strat.queue_multiplier))
            )
            state_copy.queue_state.truck_arrival_interval_min = float(
                round(state_copy.queue_state.truck_arrival_interval_min * strat.queue_multiplier, 1)
            )

            state_copy.idle_state.idle_minutes = float(
                round(state_copy.idle_state.idle_minutes * strat.idle_multiplier, 1)
            )
            state_copy.idle_state.idle_percentage = float(
                round(state_copy.idle_state.idle_percentage * strat.idle_multiplier, 1)
            )

            state_copy.productivity_state.cycle_time_sec = float(
                round(state_copy.productivity_state.cycle_time_sec * strat.cycle_time_multiplier, 1)
            )
            state_copy.machine_state.swing_angle_deg = strat.swing_angle_target_deg

            # Transition travel time added to elapsed progress
            state_copy.task_progress.elapsed_minutes += strat.transition_time_minutes

            state_copy.environment.slope_deg = max(
                0.0, float(round(state_copy.environment.slope_deg + strat.slope_modifier_deg, 1))
            )

            params = {
                "queue_multiplier": strat.queue_multiplier,
                "idle_multiplier": strat.idle_multiplier,
                "cycle_time_multiplier": strat.cycle_time_multiplier,
                "swing_angle_deg": strat.swing_angle_target_deg,
                "transition_time_minutes": strat.transition_time_minutes,
            }

            scenarios.append(CandidateScenario(
                scenario_id=scenario_id,
                action_id=strat.action_id,
                title=strat.title,
                description=strat.description,
                parameters=params,
                transformed_state=state_copy,
                explanation=strat.explanation_template,
            ))

        return scenarios


scenario_generator = TrajectoryScenarioGenerator()
