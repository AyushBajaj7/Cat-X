"""
CAT Trajectory — Next-Best-Action (NBA) Generator.
Generates up to 3 tactical recommendations prioritized by operational severity.
Core Principle: Safety recommendations strictly outrank productivity and efficiency actions.
Conforms strictly to shared/contracts/shift-twin.schema.json.
"""

from typing import List, Optional
from ..models import NextBestActionModel
from .operational_state import OperationalState


def generate_next_best_actions(
    state: OperationalState,
    has_active_decision_point: bool = False,
    attention_mode: str = "NORMAL"
) -> List[NextBestActionModel]:
    """Generates prioritized next-best-actions for the Operator Cockpit."""
    actions: List[NextBestActionModel] = []

    # 1. Safety Actions (Strictly Highest Priority)
    if not state.safety_signals.seatbelt_status:
        actions.append(NextBestActionModel(
            action_id="NBA-SAFE-01",
            title="Fasten Seatbelt Interlock",
            rationale="Seatbelt sensor detects unbuckled status during active machinery operation.",
            category="SAFETY",
            priority="CRITICAL",
            estimated_benefit="Eliminates immediate safety compliance violation and audit risk.",
        ))

    if state.safety_signals.active_proximity_hazards > 0:
        actions.append(NextBestActionModel(
            action_id="NBA-SAFE-02",
            title="Verify Swing Perimeter Clearance",
            rationale="Support vehicle or personnel detected within machine proximity envelope.",
            category="SAFETY",
            priority="CRITICAL",
            estimated_benefit="Prevents near-miss collision hazard.",
        ))

    if state.environment.slope_deg >= 13.0:
        actions.append(NextBestActionModel(
            action_id="NBA-SAFE-03",
            title="Inspect Bench Highwall Edge Stability",
            rationale=f"Current terrain grade is {state.environment.slope_deg:.1f}°, approaching stability limits.",
            category="SAFETY",
            priority="HIGH",
            estimated_benefit="Preserves track stability on saturated bench.",
        ))

    # 2. Decision & Trajectory Actions
    if has_active_decision_point or attention_mode == "DECISION_FOCUS":
        actions.append(NextBestActionModel(
            action_id="NBA-TRAJ-01",
            title="Compare Trajectory Alternatives",
            rationale="CAT Trajectory detected haul bottleneck and incoming rain front.",
            category="EFFICIENCY",
            priority="HIGH",
            estimated_benefit="Projected to recover up to 17 minutes and save 14.8L fuel.",
        ))
        actions.append(NextBestActionModel(
            action_id="NBA-TRAJ-02",
            title="Review Historical Decision Precedent",
            rationale="Operator OP1001 previously bypassed similar 4-truck queue by pre-stripping overburden.",
            category="EFFICIENCY",
            priority="NORMAL",
            estimated_benefit="Reference validated 16.5 min saving from previous shift.",
        ))

    # 3. Schedule & Shift Forecast Actions
    scheduled = state.current_task.estimated_duration_minutes
    projected = state.task_progress.elapsed_minutes + state.prediction_state.estimated_remaining_minutes
    if (projected - scheduled) >= 10.0 and len(actions) < 3:
        actions.append(NextBestActionModel(
            action_id="NBA-SCHED-01",
            title="Review Shift Forecast & Task Pacing",
            rationale=f"Completion projected {round(projected - scheduled, 1)} min past shift handoff deadline.",
            category="EFFICIENCY",
            priority="HIGH",
            estimated_benefit="Allows proactive task re-allocation before deadline is missed.",
        ))

    # 4. Idle Reduction Actions
    if state.idle_state.idle_percentage >= 15.0 and len(actions) < 3:
        actions.append(NextBestActionModel(
            action_id="NBA-IDLE-01",
            title="Reduce High-RPM Standstill Idle",
            rationale="Engine running at 1800 RPM while awaiting haul fleet arrival.",
            category="EFFICIENCY",
            priority="NORMAL",
            estimated_benefit="Saves ~0.25L diesel per minute of avoided standstill.",
        ))

    # 5. Default Fallback Actions
    if not actions:
        actions.append(NextBestActionModel(
            action_id="NBA-NOM-01",
            title="Maintain Digging Cadence",
            rationale="Current bucket cycle and slew cadence are within optimal production envelope.",
            category="EFFICIENCY",
            priority="NORMAL",
            estimated_benefit="Keeps current shift on schedule.",
        ))

    # Return up to top 3 actions
    return actions[:3]
