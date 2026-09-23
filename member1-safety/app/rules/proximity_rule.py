"""Proximity detection and buffer zone evaluation rule engine."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from ..config import settings
from ..models import (
    AlertSeverity,
    AlertType,
    IncidentType,
    ProximityWarningLevel,
    SafetyAlertModel,
    TelemetryEventInput,
)


@dataclass
class ProximityEvaluationResult:
    """Outcome of proximity rule evaluation."""

    warning_level: ProximityWarningLevel
    distance_meters: Optional[float]
    alert: Optional[SafetyAlertModel] = None
    incident_type: Optional[str] = None
    incident_severity: Optional[AlertSeverity] = None
    incident_description: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


class ProximityRule:
    """Evaluates proximity sensors against safety envelope thresholds."""

    def evaluate(self, event: TelemetryEventInput) -> ProximityEvaluationResult:
        dist = event.proximity_distance_m

        if dist is None or dist < 0:
            return ProximityEvaluationResult(
                warning_level=ProximityWarningLevel.NONE,
                distance_meters=None,
            )

        now = datetime.now(timezone.utc)
        ts_str = int(now.timestamp())
        speed_mps = event.machine_speed_mps or round(event.machine.speed_kmh / 3.6, 3)

        evidence = {
            "proximity_distance_m": dist,
            "machine_speed_mps": speed_mps,
            "critical_threshold_m": settings.proximity_critical_m,
            "high_threshold_m": settings.proximity_high_m,
            "medium_threshold_m": settings.proximity_medium_m,
            "low_threshold_m": settings.proximity_low_m,
        }

        # Tier 1: Critical proximity (< 5.0m)
        if dist < settings.proximity_critical_m:
            alert = SafetyAlertModel(
                alert_id=f"ALT-PROX-CRIT-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.PROXIMITY_HAZARD.value,
                severity=AlertSeverity.CRITICAL,
                message=f"CRITICAL: Obstacle/personnel breach at {dist:.1f}m (< {settings.proximity_critical_m}m). Halt immediately.",
                acknowledged=False,
                distance_meters=dist,
                evidence=evidence,
            )
            return ProximityEvaluationResult(
                warning_level=ProximityWarningLevel.CRITICAL,
                distance_meters=dist,
                alert=alert,
                incident_type=IncidentType.COLLISION_NEAR_MISS.value,
                incident_severity=AlertSeverity.CRITICAL,
                incident_description=f"CRITICAL: Proximity breach at {dist:.1f}m within 5m red zone envelope.",
                evidence=evidence,
            )

        # Tier 2: High proximity (< 10.0m)
        if dist < settings.proximity_high_m:
            alert = SafetyAlertModel(
                alert_id=f"ALT-PROX-HIGH-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.PROXIMITY_HAZARD.value,
                severity=AlertSeverity.HIGH,
                message=f"WARNING: Object/personnel detected at {dist:.1f}m (< {settings.proximity_high_m}m). Caution required.",
                acknowledged=False,
                distance_meters=dist,
                evidence=evidence,
            )
            # If moving into high proximity zone, log audit incident
            incident_type = IncidentType.PROXIMITY_BREACH.value if speed_mps > settings.speed_moving_threshold_mps else None
            incident_sev = AlertSeverity.HIGH if incident_type else None
            incident_desc = f"HIGH: Proximity breach at {dist:.1f}m while machine in motion ({speed_mps:.1f} m/s)" if incident_type else None

            return ProximityEvaluationResult(
                warning_level=ProximityWarningLevel.HIGH,
                distance_meters=dist,
                alert=alert,
                incident_type=incident_type,
                incident_severity=incident_sev,
                incident_description=incident_desc,
                evidence=evidence,
            )

        # Tier 3: Medium proximity (< 20.0m)
        if dist < settings.proximity_medium_m:
            alert = SafetyAlertModel(
                alert_id=f"ALT-PROX-MED-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.PROXIMITY_HAZARD.value,
                severity=AlertSeverity.MEDIUM,
                message=f"ADVISORY: Object in secondary buffer zone ({dist:.1f}m).",
                acknowledged=False,
                distance_meters=dist,
                evidence=evidence,
            )
            return ProximityEvaluationResult(
                warning_level=ProximityWarningLevel.MEDIUM,
                distance_meters=dist,
                alert=alert,
                evidence=evidence,
            )

        # Tier 4: Low proximity (< 30.0m)
        if dist < settings.proximity_low_m:
            alert = SafetyAlertModel(
                alert_id=f"ALT-PROX-LOW-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.PROXIMITY_HAZARD.value,
                severity=AlertSeverity.LOW,
                message=f"INFO: Outer perimeter vehicle detected at {dist:.1f}m.",
                acknowledged=True,
                distance_meters=dist,
                evidence=evidence,
            )
            return ProximityEvaluationResult(
                warning_level=ProximityWarningLevel.LOW,
                distance_meters=dist,
                alert=alert,
                evidence=evidence,
            )

        return ProximityEvaluationResult(
            warning_level=ProximityWarningLevel.NONE,
            distance_meters=dist,
            evidence=evidence,
        )
