"""Combined multi-factor hazard detection rule engine."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ..config import settings
from ..models import (
    AlertSeverity,
    AlertType,
    IncidentType,
    ProximityWarningLevel,
    SafetyAlertModel,
    TelemetryEventInput,
)
from .seatbelt_rule import SeatbeltEvaluationResult
from .proximity_rule import ProximityEvaluationResult


@dataclass
class CombinedHazardResult:
    """Outcome of compound multi-factor hazard evaluation."""

    is_combined_hazard: bool
    alert: Optional[SafetyAlertModel] = None
    incident_type: Optional[str] = None
    incident_severity: Optional[AlertSeverity] = None
    incident_description: Optional[str] = None
    contributing_factors: List[str] = None
    evidence: Optional[Dict[str, Any]] = None


class CombinedHazardRule:
    """Detects correlated multi-factor hazards requiring immediate intervention."""

    def evaluate(
        self,
        event: TelemetryEventInput,
        seatbelt_res: SeatbeltEvaluationResult,
        proximity_res: ProximityEvaluationResult,
    ) -> CombinedHazardResult:
        factors = []
        now = datetime.now(timezone.utc)
        ts_str = int(now.timestamp())

        # Factor 1: Seatbelt non-compliance
        if not seatbelt_res.is_compliant:
            factors.append("SEATBELT_UNBUCKLED")

        # Factor 2: Proximity hazard (HIGH or CRITICAL)
        if proximity_res.warning_level in (ProximityWarningLevel.HIGH, ProximityWarningLevel.CRITICAL):
            dist = proximity_res.distance_meters or 0.0
            factors.append(f"PROXIMITY_HAZARD_{proximity_res.warning_level.value} ({dist:.1f}m)")

        # Factor 3: High speed or tramming
        speed_mps = event.machine_speed_mps or round(event.machine.speed_kmh / 3.6, 3)
        if speed_mps >= settings.speed_tramming_threshold_mps:
            factors.append(f"HIGH_SPEED_TRAMMING ({speed_mps:.1f} m/s)")

        # Factor 4: Operator fatigue
        fatigue = event.operator.fatigue_score
        if fatigue >= settings.fatigue_warning_score:
            factors.append(f"ELEVATED_FATIGUE ({fatigue:.1f})")

        # Check for combined conditions
        # Condition A: Unbuckled + Proximity Hazard
        unbuckled_and_prox = (
            "SEATBELT_UNBUCKLED" in factors
            and any("PROXIMITY_HAZARD" in f for f in factors)
        )

        # Condition B: High Speed + Proximity Hazard
        speed_and_prox = (
            any("HIGH_SPEED_TRAMMING" in f for f in factors)
            and any("PROXIMITY_HAZARD" in f for f in factors)
        )

        # Condition C: Unbuckled + Elevated Fatigue
        unbuckled_and_fatigue = (
            "SEATBELT_UNBUCKLED" in factors
            and any("ELEVATED_FATIGUE" in f for f in factors)
        )

        if unbuckled_and_prox or speed_and_prox or unbuckled_and_fatigue:
            evidence = {
                "contributing_factors": factors,
                "seatbelt_fastened": seatbelt_res.is_compliant,
                "proximity_distance_m": proximity_res.distance_meters,
                "machine_speed_mps": speed_mps,
                "fatigue_score": fatigue,
                "compound_rule_triggered": (
                    "UNBUCKLED_WITH_PROXIMITY"
                    if unbuckled_and_prox
                    else "HIGH_SPEED_WITH_PROXIMITY"
                    if speed_and_prox
                    else "UNBUCKLED_WITH_FATIGUE"
                ),
            }

            alert = SafetyAlertModel(
                alert_id=f"ALT-COMBINED-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.COMBINED_HAZARD.value,
                severity=AlertSeverity.CRITICAL,
                message=(
                    f"CRITICAL COMBINED HAZARD: Multiple concurrent safety violations detected: {', '.join(factors)}. "
                    "Emergency caution required."
                ),
                acknowledged=False,
                distance_meters=proximity_res.distance_meters,
                evidence=evidence,
            )

            return CombinedHazardResult(
                is_combined_hazard=True,
                alert=alert,
                incident_type=IncidentType.COMBINED_HAZARD.value,
                incident_severity=AlertSeverity.CRITICAL,
                incident_description=f"CRITICAL COMBINED HAZARD: Correlated violations: {'; '.join(factors)}",
                contributing_factors=factors,
                evidence=evidence,
            )

        return CombinedHazardResult(
            is_combined_hazard=False,
            contributing_factors=factors,
        )
