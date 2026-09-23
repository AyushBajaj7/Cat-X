"""Seatbelt compliance evaluation rule engine."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from ..config import settings
from ..models import (
    AlertSeverity,
    AlertType,
    IncidentType,
    SafetyAlertModel,
    TelemetryEventInput,
)


@dataclass
class SeatbeltEvaluationResult:
    """Outcome of seatbelt rule evaluation."""

    is_compliant: bool
    compliance_pct: float
    alert: Optional[SafetyAlertModel] = None
    incident_type: Optional[str] = None
    incident_severity: Optional[AlertSeverity] = None
    incident_description: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


class SeatbeltRule:
    """Evaluates operator seatbelt status against machine kinetic state."""

    def __init__(self):
        # In-memory history for rolling compliance calculation: operator_id -> (fastened_count, total_count)
        self._history: Dict[str, tuple[int, int]] = {}

    def evaluate(self, event: TelemetryEventInput) -> SeatbeltEvaluationResult:
        fastened = event.operator.seatbelt_fastened
        if event.seatbelt_status is not None:
            fastened = (event.seatbelt_status.upper() == "BUCKLED")

        # Update historical compliance counter
        fastened_count, total_count = self._history.get(event.operator_id, (0, 0))
        total_count += 1
        if fastened:
            fastened_count += 1
        self._history[event.operator_id] = (fastened_count, total_count)
        compliance_pct = round((fastened_count / total_count) * 100.0, 1)

        speed_mps = event.machine_speed_mps
        if speed_mps is None:
            speed_mps = round(event.machine.speed_kmh / 3.6, 3)

        machine_state = (event.machine_state or "WORKING").upper()

        if fastened:
            return SeatbeltEvaluationResult(
                is_compliant=True,
                compliance_pct=compliance_pct,
                evidence={
                    "seatbelt_fastened": True,
                    "machine_speed_mps": speed_mps,
                    "machine_state": machine_state,
                    "compliance_pct": compliance_pct,
                },
            )

        # Seatbelt is UNBUCKLED - evaluate hazard severity based on kinetic motion
        now = datetime.now(timezone.utc)
        ts_str = int(now.timestamp())
        evidence = {
            "seatbelt_fastened": False,
            "machine_speed_mps": speed_mps,
            "machine_state": machine_state,
            "compliance_pct": compliance_pct,
            "tramming_threshold_mps": settings.speed_tramming_threshold_mps,
            "moving_threshold_mps": settings.speed_moving_threshold_mps,
        }

        if machine_state == "TRAMMING" or speed_mps >= settings.speed_tramming_threshold_mps:
            # High kinetic energy motion unbuckled -> CRITICAL alert + incident
            alert = SafetyAlertModel(
                alert_id=f"ALT-SB-CRIT-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.SEATBELT_UNBUCKLED.value,
                severity=AlertSeverity.CRITICAL,
                message=f"Operator unbuckled while machine is tramming at speed ({speed_mps:.1f} m/s)",
                acknowledged=False,
                evidence=evidence,
            )
            return SeatbeltEvaluationResult(
                is_compliant=False,
                compliance_pct=compliance_pct,
                alert=alert,
                incident_type=IncidentType.SEATBELT_VIOLATION.value,
                incident_severity=AlertSeverity.CRITICAL,
                incident_description=f"CRITICAL: Unbuckled while tramming at {speed_mps:.1f} m/s",
                evidence=evidence,
            )

        if machine_state == "WORKING" or speed_mps >= settings.speed_moving_threshold_mps:
            # Active work cycle motion unbuckled -> HIGH alert + incident
            alert = SafetyAlertModel(
                alert_id=f"ALT-SB-HIGH-{event.operator_id}-{ts_str}",
                timestamp=now,
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type=AlertType.SEATBELT_UNBUCKLED.value,
                severity=AlertSeverity.HIGH,
                message=f"Operator unbuckled during active work motion ({speed_mps:.1f} m/s)",
                acknowledged=False,
                evidence=evidence,
            )
            return SeatbeltEvaluationResult(
                is_compliant=False,
                compliance_pct=compliance_pct,
                alert=alert,
                incident_type=IncidentType.SEATBELT_VIOLATION.value,
                incident_severity=AlertSeverity.HIGH,
                incident_description=f"HIGH: Unbuckled during work cycle motion ({speed_mps:.1f} m/s)",
                evidence=evidence,
            )

        # Machine is stopped or idle -> MEDIUM advisory alert (no automated incident)
        alert = SafetyAlertModel(
            alert_id=f"ALT-SB-MED-{event.operator_id}-{ts_str}",
            timestamp=now,
            operator_id=event.operator_id,
            machine_id=event.machine_id,
            alert_type=AlertType.SEATBELT_UNBUCKLED.value,
            severity=AlertSeverity.MEDIUM,
            message="Seatbelt unbuckled while machine is stationary in gear",
            acknowledged=False,
            evidence=evidence,
        )
        return SeatbeltEvaluationResult(
            is_compliant=False,
            compliance_pct=compliance_pct,
            alert=alert,
            evidence=evidence,
        )
