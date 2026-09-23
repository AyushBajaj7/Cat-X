"""Safety Service business logic skeleton (Owned by Engineer 1)."""

from datetime import datetime, timezone
from typing import List, Optional
from .models import (
    AlertSeverity,
    BehaviourAnalysisModel,
    IncidentModel,
    ProximityWarningLevel,
    SafetyAlertModel,
    SafetyStatusModel,
    TelemetryEventInput,
)


class SafetyService:
    """Core logic layer for safety evaluation, alerting, and behavior tracking."""

    def __init__(self):
        self._alerts: List[SafetyAlertModel] = []
        self._incidents: List[IncidentModel] = []
        self._operator_statuses: dict[str, SafetyStatusModel] = {}
        self._operator_behaviours: dict[str, BehaviourAnalysisModel] = {}

    def process_telemetry(self, event: TelemetryEventInput) -> SafetyStatusModel:
        """Evaluate incoming telemetry event for safety violations and behavior flags."""
        seatbelt = event.operator.seatbelt_fastened
        fatigue = event.operator.fatigue_score
        speed = event.machine.speed_kmh

        warning_level = ProximityWarningLevel.NONE
        active_hazards = 0
        safety_score = 100.0

        if not seatbelt:
            safety_score -= 20.0
            alert = SafetyAlertModel(
                alert_id=f"ALT-SB-{int(datetime.now(timezone.utc).timestamp())}",
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                alert_type="SEATBELT_UNBUCKLED",
                severity=AlertSeverity.HIGH if speed > 5.0 else AlertSeverity.MEDIUM,
                message="Seatbelt unbuckled while machine is operating",
                acknowledged=False,
            )
            self._alerts.append(alert)

        if fatigue > 75.0:
            safety_score -= 15.0

        status = SafetyStatusModel(
            operator_id=event.operator_id,
            machine_id=event.machine_id,
            timestamp=datetime.now(timezone.utc),
            seatbelt_fastened=seatbelt,
            seatbelt_compliance_pct=95.0 if seatbelt else 75.0,
            proximity_warning_level=warning_level,
            active_hazard_count=active_hazards,
            overall_safety_score=max(0.0, safety_score),
        )
        self._operator_statuses[event.operator_id] = status
        return status

    def get_status(self, operator_id: str) -> SafetyStatusModel:
        """Retrieve latest safety status for operator."""
        if operator_id in self._operator_statuses:
            return self._operator_statuses[operator_id]
        return SafetyStatusModel(
            operator_id=operator_id,
            machine_id="EXC-CAT-001",
            timestamp=datetime.now(timezone.utc),
            seatbelt_fastened=True,
            seatbelt_compliance_pct=98.5,
            proximity_warning_level=ProximityWarningLevel.NONE,
            active_hazard_count=0,
            overall_safety_score=97.0,
        )

    def get_alerts(self, operator_id: str, severity: Optional[str] = None) -> List[SafetyAlertModel]:
        """List active alerts for operator."""
        matching = [a for a in self._alerts if a.operator_id == operator_id]
        if severity:
            matching = [a for a in matching if a.severity.value == severity]
        if not matching:
            return [
                SafetyAlertModel(
                    alert_id=f"ALT-INIT-{operator_id}",
                    operator_id=operator_id,
                    machine_id="EXC-CAT-001",
                    alert_type="PROXIMITY_HAZARD",
                    severity=AlertSeverity.LOW,
                    message="Support vehicle entering 15m perimeter buffer zone",
                    acknowledged=True,
                    distance_meters=14.2,
                )
            ]
        return matching

    def get_incidents(self, operator_id: str) -> List[IncidentModel]:
        """List audit incident logs for operator."""
        matching = [i for i in self._incidents if i.operator_id == operator_id]
        if not matching:
            return [
                IncidentModel(
                    incident_id="INC-LOG-001",
                    operator_id=operator_id,
                    machine_id="EXC-CAT-001",
                    task_id="T001",
                    incident_type="SEATBELT_VIOLATION",
                    severity=AlertSeverity.MEDIUM,
                    description="Unbuckled during engine idle phase before cycle start",
                    logged_by="SYSTEM_AUTOMATED",
                )
            ]
        return matching

    def get_behaviour_analysis(self, operator_id: str) -> BehaviourAnalysisModel:
        """Retrieve behavior scores and flags."""
        if operator_id in self._operator_behaviours:
            return self._operator_behaviours[operator_id]
        return BehaviourAnalysisModel(
            analysis_id=f"BA-{operator_id}-001",
            operator_id=operator_id,
            timestamp=datetime.now(timezone.utc),
            excessive_idling_score=14.0,
            aggressive_maneuver_count=0,
            unsafe_speed_events=0,
            cycle_consistency_pct=91.5,
            overall_behaviour_score=93.5,
            flags=["MINOR_IDLE_BURST"],
        )


safety_service = SafetyService()
