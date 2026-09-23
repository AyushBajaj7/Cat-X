"""
CAT Trajectory — Safety Constraint Engine.
Core Principle: SAFETY IS A CONSTRAINT, NOT A PRODUCTIVITY PENALTY.

Evaluates candidate trajectories against deterministic physical and site safety limits.
Hard constraints are checked FIRST: if any hard constraint is breached, the trajectory
status is set to REJECTED. Infeasible scenarios cannot be recommended.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from ..domain.operational_state import OperationalState


class ConstraintReportItem(BaseModel):
    """Detailed evaluation of an individual safety constraint."""
    constraint_id: str
    name: str
    is_hard_constraint: bool = True
    status: str  # PASS, WARNING, VIOLATED
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    value: float
    threshold: float
    unit: str
    explanation: str


class ConstraintValidationResult(BaseModel):
    """Outcome of constraint evaluation for a candidate scenario."""
    scenario_id: str
    constraint_status: str  # FEASIBLE, REJECTED
    constraints: List[ConstraintReportItem]
    rejection_reasons: List[str] = Field(default_factory=list)
    composite_safety_risk_score: float = 10.0  # 0 to 100 scale


# Prototype Operational Safety Thresholds (calibrated to heavy equipment standards)
SAFETY_THRESHOLDS = {
    "MAX_STABLE_SLOPE_DEG": 15.0,        # Hard limit: rollover danger above 15.0°
    "WARNING_SLOPE_DEG": 12.0,           # Warning margin
    "MIN_PROXIMITY_DISTANCE_M": 10.0,    # Hard limit: 10m danger envelope
    "WARNING_PROXIMITY_M": 15.0,         # Warning buffer: 15m
    "MIN_HIGHWALL_SETBACK_M": 4.0,       # Hard limit: 4.0m from crest edge
    "WARNING_HIGHWALL_SETBACK_M": 5.5,   # Warning setback
    "MAX_PAYLOAD_PERCENT": 108.0,        # Hard limit: 108% of rated tonnage
}


class SafetyConstraintEngine:
    """Deterministic hard-gate safety validator."""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or SAFETY_THRESHOLDS

    def validate_scenario(
        self,
        scenario_id: str,
        state: OperationalState,
        overrides: Optional[Dict[str, Any]] = None
    ) -> ConstraintValidationResult:
        """
        Validates transformed scenario state against physical constraints.
        Returns FEASIBLE or REJECTED with full explainable evidence.
        """
        overrides = overrides or {}
        items: List[ConstraintReportItem] = []
        rejection_reasons: List[str] = []

        # 1. Slope Constraint (CST-SLOPE-01)
        slope = overrides.get("slope_deg", state.environment.slope_deg)
        max_slope = self.thresholds["MAX_STABLE_SLOPE_DEG"]
        warn_slope = self.thresholds["WARNING_SLOPE_DEG"]

        if slope > max_slope:
            slope_status = "VIOLATED"
            slope_sev = "CRITICAL"
            reason = f"Slope {slope:.1f}° exceeds absolute machine stability limit of {max_slope:.1f}°."
            rejection_reasons.append(reason)
        elif slope >= warn_slope:
            slope_status = "WARNING"
            slope_sev = "HIGH"
            reason = f"Slope {slope:.1f}° enters elevated stability watch zone (threshold {warn_slope:.1f}°)."
        else:
            slope_status = "PASS"
            slope_sev = "LOW"
            reason = f"Slope {slope:.1f}° within safe operating envelope (<{warn_slope:.1f}°)."

        items.append(ConstraintReportItem(
            constraint_id="CST-SLOPE-01",
            name="Ground Stability & Terrain Grade",
            is_hard_constraint=True,
            status=slope_status,
            severity=slope_sev,
            value=float(slope),
            threshold=float(max_slope),
            unit="deg",
            explanation=reason,
        ))

        # 2. Proximity Margin Constraint (CST-PROXIMITY-01)
        # Check active proximity flags from Engineer 1
        hazards = state.safety_signals.active_proximity_hazards
        min_prox = self.thresholds["MIN_PROXIMITY_DISTANCE_M"]
        est_prox = overrides.get("proximity_distance_m", 25.0 if hazards == 0 else 8.0)

        if est_prox < min_prox or hazards > 1:
            prox_status = "VIOLATED"
            prox_sev = "CRITICAL"
            reason = f"Obstacle or support vehicle at {est_prox:.1f}m inside 10.0m exclusion envelope."
            rejection_reasons.append(reason)
        elif est_prox < self.thresholds["WARNING_PROXIMITY_M"] or hazards == 1:
            prox_status = "WARNING"
            prox_sev = "MEDIUM"
            reason = f"Proximity buffer reduced to {est_prox:.1f}m (warning threshold 15.0m)."
        else:
            prox_status = "PASS"
            prox_sev = "LOW"
            reason = f"Proximity buffer clear at {est_prox:.1f}m."

        items.append(ConstraintReportItem(
            constraint_id="CST-PROXIMITY-01",
            name="Fleet & Personnel Proximity Envelope",
            is_hard_constraint=True,
            status=prox_status,
            severity=prox_sev,
            value=float(est_prox),
            threshold=float(min_prox),
            unit="meters",
            explanation=reason,
        ))

        # 3. Highwall Crest Setback (CST-HIGHWALL-01)
        highwall_setback = overrides.get("highwall_setback_m", 6.5)
        min_setback = self.thresholds["MIN_HIGHWALL_SETBACK_M"]

        if highwall_setback < min_setback:
            hw_status = "VIOLATED"
            hw_sev = "CRITICAL"
            reason = f"Machine tracks positioned {highwall_setback:.1f}m from crest edge (<{min_setback:.1f}m limit)."
            rejection_reasons.append(reason)
        elif highwall_setback < self.thresholds["WARNING_HIGHWALL_SETBACK_M"]:
            hw_status = "WARNING"
            hw_sev = "HIGH"
            reason = f"Machine tracks within warning zone {highwall_setback:.1f}m from crest."
        else:
            hw_status = "PASS"
            hw_sev = "LOW"
            reason = f"Highwall setback maintained at safe {highwall_setback:.1f}m margin."

        items.append(ConstraintReportItem(
            constraint_id="CST-HIGHWALL-01",
            name="Bench Crest Setback",
            is_hard_constraint=True,
            status=hw_status,
            severity=hw_sev,
            value=float(highwall_setback),
            threshold=float(min_setback),
            unit="meters",
            explanation=reason,
        ))

        # 4. Seatbelt Compliance Constraint (CST-SEATBELT-01)
        seatbelt_fastened = overrides.get("seatbelt_status", state.safety_signals.seatbelt_status)
        if not seatbelt_fastened:
            sb_status = "VIOLATED"
            sb_sev = "CRITICAL"
            reason = "Mandatory seatbelt interlock unbuckled while machine active."
            rejection_reasons.append(reason)
        else:
            sb_status = "PASS"
            sb_sev = "LOW"
            reason = "Seatbelt fastened and compliant."

        items.append(ConstraintReportItem(
            constraint_id="CST-SEATBELT-01",
            name="Operator Seatbelt Compliance",
            is_hard_constraint=True,
            status=sb_status,
            severity=sb_sev,
            value=1.0 if seatbelt_fastened else 0.0,
            threshold=1.0,
            unit="boolean",
            explanation=reason,
        ))

        # 5. Determine Overall Feasibility
        is_rejected = any(item.status == "VIOLATED" for item in items)
        constraint_status = "REJECTED" if is_rejected else "FEASIBLE"

        # Calculate composite safety risk score (0 to 100)
        # Violated hard constraint immediately yields 85-100 risk score
        if is_rejected:
            risk_score = 92.0
        else:
            warning_count = sum(1 for item in items if item.status == "WARNING")
            risk_score = min(45.0, 10.0 + (warning_count * 12.0))

        return ConstraintValidationResult(
            scenario_id=scenario_id,
            constraint_status=constraint_status,
            constraints=items,
            rejection_reasons=rejection_reasons,
            composite_safety_risk_score=risk_score,
        )


safety_constraint_engine = SafetyConstraintEngine()
