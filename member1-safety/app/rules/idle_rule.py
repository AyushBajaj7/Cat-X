"""Excessive idling evaluation rule engine.

NOTE: Idling is classified as behaviour intelligence and fuel efficiency
monitoring, not an acute life-safety violation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ..config import settings
from ..models import (
    AlertSeverity,
    AlertType,
    SafetyAlertModel,
    TelemetryEventInput,
)


@dataclass
class IdleEvaluationResult:
    """Outcome of idling evaluation."""

    idle_minutes: float
    is_excessive: bool
    idle_score: float  # 0 - 100 percentage
    fuel_wasted_l: float
    flags: List[str]
    alert: Optional[SafetyAlertModel] = None
    evidence: Optional[Dict[str, Any]] = None


class IdleRule:
    """Evaluates stationary engine run times against operational efficiency thresholds."""

    def evaluate(self, event: TelemetryEventInput) -> IdleEvaluationResult:
        idle_min = event.idle_minutes if event.idle_minutes is not None else 0.0
        fuel_rate = event.fuel_rate_lph or event.machine.fuel_rate_lph or 15.0

        fuel_wasted_l = round(idle_min * (fuel_rate / 60.0), 2)
        idle_score = min(100.0, round((idle_min / 60.0) * 100.0, 1))

        flags: List[str] = []
        alert: Optional[SafetyAlertModel] = None
        now = datetime.now(timezone.utc)
        ts_str = int(now.timestamp())

        evidence = {
            "idle_minutes": idle_min,
            "fuel_rate_lph": fuel_rate,
            "estimated_fuel_wasted_l": fuel_wasted_l,
            "warning_threshold_min": settings.idle_warning_minutes,
            "critical_threshold_min": settings.idle_critical_minutes,
        }

        if idle_min >= settings.idle_critical_minutes:
            flags.append("EXCESSIVE_IDLE_CRITICAL")
            alert = SafetyAlertModel(
                alert_id=f"ALT-IDLE-CRIT-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.EXCESSIVE_IDLE.value,
                severity=AlertSeverity.MEDIUM,
                message=(
                    f"Excessive idle detected: {idle_min:.1f} minutes (> {settings.idle_critical_minutes} min). "
                    f"Estimated {fuel_wasted_l:.1f}L fuel consumed unproductively. Recommend engine shutdown or task reassignment."
                ),
                acknowledged=False,
                evidence=evidence,
            )
            return IdleEvaluationResult(
                idle_minutes=idle_min,
                is_excessive=True,
                idle_score=idle_score,
                fuel_wasted_l=fuel_wasted_l,
                flags=flags,
                alert=alert,
                evidence=evidence,
            )

        if idle_min >= settings.idle_warning_minutes:
            flags.append("EXCESSIVE_IDLE_WARNING")
            alert = SafetyAlertModel(
                alert_id=f"ALT-IDLE-WARN-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.EXCESSIVE_IDLE.value,
                severity=AlertSeverity.LOW,
                message=(
                    f"Idle advisory: {idle_min:.1f} minutes stationary (> {settings.idle_warning_minutes} min). "
                    f"Consider eco-mode or queue check."
                ),
                acknowledged=True,
                evidence=evidence,
            )
            return IdleEvaluationResult(
                idle_minutes=idle_min,
                is_excessive=True,
                idle_score=idle_score,
                fuel_wasted_l=fuel_wasted_l,
                flags=flags,
                alert=alert,
                evidence=evidence,
            )

        return IdleEvaluationResult(
            idle_minutes=idle_min,
            is_excessive=False,
            idle_score=idle_score,
            fuel_wasted_l=fuel_wasted_l,
            flags=flags,
            evidence=evidence,
        )
