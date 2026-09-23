"""Comprehensive Safety Service coordination layer (Owned by Engineer 1)."""

from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional
from .behaviour import (
    AnomalyEngine,
    BaselineManager,
    FeatureExtractor,
    TrendAnalyzer,
)
from .database import SessionLocal
from .db_models import (
    BehaviourMetricORM,
    SafetyAlertORM,
    SafetyEventORM,
)
from .incidents import IncidentManager
from .models import (
    AlertSeverity,
    BehaviourAnalysisModel,
    ConstraintSignal,
    IncidentModel,
    ProximityWarningLevel,
    SafetyAlertModel,
    SafetyState,
    SafetyStatusModel,
    TelemetryEventInput,
)
from .rules import (
    CombinedHazardRule,
    ConstraintGenerator,
    IdleRule,
    ProximityRule,
    SeatbeltRule,
)

logger = logging.getLogger("safety.service")


class SafetyService:
    """
    Coordinates telemetry ingestion, rule evaluation, incident management,
    behavioral anomaly detection, and trajectory constraint generation.
    """

    def __init__(self):
        # Subsystems
        self.seatbelt_rule = SeatbeltRule()
        self.proximity_rule = ProximityRule()
        self.combined_rule = CombinedHazardRule()
        self.idle_rule = IdleRule()
        self.constraint_gen = ConstraintGenerator()
        self.incident_manager = IncidentManager()

        # Behaviour intelligence
        self.baseline_manager = BaselineManager()
        self.anomaly_engine = AnomalyEngine()
        self.trend_analyzer = TrendAnalyzer()

        # In-memory stores
        self._alerts: List[SafetyAlertModel] = []
        self._operator_statuses: Dict[str, SafetyStatusModel] = {}
        self._operator_telemetry_history: Dict[str, List[TelemetryEventInput]] = {}
        self._active_constraints: Dict[str, List[ConstraintSignal]] = {}

    def process_telemetry(self, event: TelemetryEventInput) -> SafetyStatusModel:
        """
        Evaluate incoming telemetry against all safety rules, log incidents,
        emit Trajectory constraints, and compute deterministic safety status.
        """
        # 1. Track rolling telemetry window for operator (up to 50 events)
        op_id = event.operator_id
        if op_id not in self._operator_telemetry_history:
            self._operator_telemetry_history[op_id] = []
        self._operator_telemetry_history[op_id].append(event)
        if len(self._operator_telemetry_history[op_id]) > 50:
            self._operator_telemetry_history[op_id] = self._operator_telemetry_history[op_id][-50:]

        # 2. Evaluate individual and compound rules
        seatbelt_res = self.seatbelt_rule.evaluate(event)
        proximity_res = self.proximity_rule.evaluate(event)
        combined_res = self.combined_rule.evaluate(event, seatbelt_res, proximity_res)
        idle_res = self.idle_rule.evaluate(event)

        # 3. Collect active alerts
        current_alerts: List[SafetyAlertModel] = []
        if combined_res.is_combined_hazard and combined_res.alert:
            current_alerts.append(combined_res.alert)
        else:
            if seatbelt_res.alert:
                current_alerts.append(seatbelt_res.alert)
            if proximity_res.alert:
                current_alerts.append(proximity_res.alert)

        if idle_res.alert:
            current_alerts.append(idle_res.alert)

        # Store alerts and persist
        for alt in current_alerts:
            self._alerts.append(alt)
            self._persist_alert(alt)

        # 4. Log incidents via IncidentManager with deduplication
        if combined_res.is_combined_hazard and combined_res.incident_type:
            self.incident_manager.log_incident(
                operator_id=event.operator_id,
                machine_id=event.machine_id,
                incident_type=combined_res.incident_type,
                severity=combined_res.incident_severity or AlertSeverity.CRITICAL,
                description=combined_res.incident_description or "Combined hazard incident",
                task_id=event.task_id,
                evidence=combined_res.evidence,
            )
        else:
            if seatbelt_res.incident_type:
                self.incident_manager.log_incident(
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    incident_type=seatbelt_res.incident_type,
                    severity=seatbelt_res.incident_severity or AlertSeverity.HIGH,
                    description=seatbelt_res.incident_description or "Seatbelt violation incident",
                    task_id=event.task_id,
                    evidence=seatbelt_res.evidence,
                )
            if proximity_res.incident_type:
                self.incident_manager.log_incident(
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    incident_type=proximity_res.incident_type,
                    severity=proximity_res.incident_severity or AlertSeverity.HIGH,
                    description=proximity_res.incident_description or "Proximity hazard incident",
                    task_id=event.task_id,
                    evidence=proximity_res.evidence,
                )

        # 5. Generate Trajectory Constraints
        constraints = self.constraint_gen.generate_constraints(
            event, seatbelt_res, proximity_res, combined_res, idle_res
        )
        self._active_constraints[op_id] = constraints

        # 6. Compute Deterministic Safety State and Overall Safety Score
        score = 100.0

        if not seatbelt_res.is_compliant:
            score -= 20.0

        prox_deductions = {
            ProximityWarningLevel.CRITICAL: 35.0,
            ProximityWarningLevel.HIGH: 20.0,
            ProximityWarningLevel.MEDIUM: 10.0,
            ProximityWarningLevel.LOW: 5.0,
            ProximityWarningLevel.NONE: 0.0,
        }
        score -= prox_deductions.get(proximity_res.warning_level, 0.0)

        if combined_res.is_combined_hazard:
            score -= 30.0

        fatigue = event.operator.fatigue_score
        if fatigue >= 85.0:
            score -= 20.0
        elif fatigue >= 70.0:
            score -= 10.0

        safety_score = max(0.0, min(100.0, round(score, 1)))

        # Deterministic Safety State: strictly SAFE / WARNING / HIGH_RISK
        if (
            combined_res.is_combined_hazard
            or proximity_res.warning_level == ProximityWarningLevel.CRITICAL
            or (not seatbelt_res.is_compliant and event.machine_speed_mps and event.machine_speed_mps >= 2.0)
            or safety_score < 60.0
        ):
            safety_state = SafetyState.HIGH_RISK
        elif (
            proximity_res.warning_level in (ProximityWarningLevel.HIGH, ProximityWarningLevel.MEDIUM)
            or not seatbelt_res.is_compliant
            or idle_res.is_excessive
            or safety_score < 85.0
        ):
            safety_state = SafetyState.WARNING
        else:
            safety_state = SafetyState.SAFE

        # Active hazard count: distinct unacknowledged alerts currently threatening safe operation
        active_hazards = len(current_alerts)

        status = SafetyStatusModel(
            operator_id=event.operator_id,
            machine_id=event.machine_id,
            timestamp=datetime.now(timezone.utc),
            seatbelt_fastened=seatbelt_res.is_compliant,
            seatbelt_compliance_pct=seatbelt_res.compliance_pct,
            proximity_warning_level=proximity_res.warning_level,
            active_hazard_count=active_hazards,
            overall_safety_score=safety_score,
            safety_state=safety_state,
            active_alerts=current_alerts,
            active_constraints=constraints,
        )

        self._operator_statuses[op_id] = status
        self._persist_telemetry_event(event)

        return status

    def get_status(self, operator_id: str) -> SafetyStatusModel:
        """Retrieve current safety status for an operator."""
        if operator_id in self._operator_statuses:
            return self._operator_statuses[operator_id]

        # Nominal fallback for unobserved operator
        return SafetyStatusModel(
            operator_id=operator_id,
            machine_id="EXC-CAT-001",
            timestamp=datetime.now(timezone.utc),
            seatbelt_fastened=True,
            seatbelt_compliance_pct=98.5,
            proximity_warning_level=ProximityWarningLevel.NONE,
            active_hazard_count=0,
            overall_safety_score=98.0,
            safety_state=SafetyState.SAFE,
            active_alerts=[],
            active_constraints=[],
        )

    def get_alerts(
        self, operator_id: str, severity: Optional[str] = None
    ) -> List[SafetyAlertModel]:
        """List active alerts for an operator, with optional severity filter."""
        matching = [a for a in self._alerts if a.operator_id == operator_id]
        if severity:
            matching = [a for a in matching if a.severity.value == severity]

        if not matching:
            # If no alerts in memory, return an empty list or nominal default if first query
            return []

        # Return sorted descending by timestamp
        matching.sort(key=lambda x: x.timestamp, reverse=True)
        return matching

    def get_incidents(
        self, operator_id: str, status: Optional[str] = None
    ) -> List[IncidentModel]:
        """Retrieve audit incident logs for an operator."""
        incidents = self.incident_manager.get_incidents(operator_id=operator_id, status=status)
        return incidents

    def acknowledge_incident(
        self, incident_id: str, acknowledged_by: str = "SUPERVISOR_CONSOLE"
    ) -> Optional[IncidentModel]:
        """Acknowledge an incident by ID."""
        return self.incident_manager.acknowledge_incident(incident_id, acknowledged_by)

    def resolve_incident(
        self,
        incident_id: str,
        resolved_by: str = "SUPERVISOR_CONSOLE",
        resolution_notes: str = "",
    ) -> Optional[IncidentModel]:
        """Resolve an incident by ID."""
        return self.incident_manager.resolve_incident(
            incident_id, resolved_by, resolution_notes
        )

    def get_behaviour_analysis(self, operator_id: str) -> BehaviourAnalysisModel:
        """
        Evaluate operator rolling behavior, compute IsolationForest anomaly index,
        and generate Trajectory constraint flags.
        """
        events = self._operator_telemetry_history.get(operator_id, [])
        features = FeatureExtractor.extract_features(events)

        # Update baseline and identify outlier signals
        self.baseline_manager.update_baseline(operator_id, features)
        signals = self.baseline_manager.detect_signals(operator_id, features)

        # Anomaly scoring
        anomaly_res = self.anomaly_engine.score(features)

        # Multi-axis trends
        self.trend_analyzer.record_snapshot(operator_id, features)
        trends = self.trend_analyzer.analyze_trends(operator_id)

        # Flags & constraint signals
        flags: List[str] = []
        if features.idle_ratio > 0.35:
            flags.append("EXCESSIVE_IDLE_BURST")
        if features.seatbelt_compliance_pct < 90.0:
            flags.append("SEATBELT_COMPLIANCE_BELOW_TARGET")
        if features.aggressive_maneuver_count > 0:
            flags.append(f"AGGRESSIVE_THROTTLE_TRANSITIONS_{features.aggressive_maneuver_count}")
        if features.mean_fatigue > 60.0:
            flags.append("ELEVATED_OPERATOR_FATIGUE")
        if anomaly_res.anomaly_detected:
            flags.append("OPERATIONAL_PATTERN_ANOMALY")

        constraint_flags: List[str] = []
        active_constraints = self._active_constraints.get(operator_id, [])
        for c in active_constraints:
            constraint_flags.append(f"{c.constraint_type}_{c.severity.value}")

        # Overall composite behaviour score (efficiency + consistency + discipline)
        base_score = 100.0
        base_score -= (features.idle_ratio * 40.0)
        base_score -= (features.aggressive_maneuver_count * 5.0)
        base_score -= (features.unsafe_speed_events * 10.0)
        if features.cycle_consistency_pct < 90.0:
            base_score -= (90.0 - features.cycle_consistency_pct) * 0.5
        overall_score = max(0.0, min(100.0, round(base_score, 1)))

        analysis = BehaviourAnalysisModel(
            analysis_id=f"BA-{operator_id}-{int(datetime.now(timezone.utc).timestamp())}",
            operator_id=operator_id,
            machine_id=events[-1].machine_id if events else "EXC-CAT-001",
            timestamp=datetime.now(timezone.utc),
            excessive_idling_score=round(features.idle_ratio * 100.0, 1),
            aggressive_maneuver_count=features.aggressive_maneuver_count,
            unsafe_speed_events=features.unsafe_speed_events,
            cycle_consistency_pct=features.cycle_consistency_pct,
            overall_behaviour_score=overall_score,
            flags=flags,
            anomaly_detected=anomaly_res.anomaly_detected,
            constraint_flags=constraint_flags,
            anomaly_score=anomaly_res.anomaly_score,
            trends=trends.to_dict(),
            signals=signals,
        )

        self._persist_behaviour_metric(analysis)
        return analysis

    def _persist_alert(self, alert: SafetyAlertModel):
        try:
            with SessionLocal() as db:
                orm_obj = SafetyAlertORM(
                    alert_id=alert.alert_id,
                    timestamp=alert.timestamp,
                    operator_id=alert.operator_id,
                    machine_id=alert.machine_id,
                    alert_type=alert.alert_type,
                    severity=alert.severity.value,
                    message=alert.message,
                    acknowledged=alert.acknowledged,
                    distance_meters=alert.distance_meters,
                    evidence=alert.evidence,
                )
                db.add(orm_obj)
                db.commit()
        except Exception as e:
            logger.debug(f"DB alert insert skipped or failed: {e}")

    def _persist_telemetry_event(self, event: TelemetryEventInput):
        try:
            with SessionLocal() as db:
                orm_obj = SafetyEventORM(
                    event_id=event.event_id,
                    timestamp=event.timestamp,
                    operator_id=event.operator_id,
                    machine_id=event.machine_id,
                    task_id=event.task_id,
                    speed_mps=event.machine_speed_mps or 0.0,
                    seatbelt_status=event.seatbelt_status or "BUCKLED",
                    proximity_distance_m=event.proximity_distance_m,
                    idle_minutes=event.idle_minutes,
                    machine_state=event.machine_state,
                    raw_payload=event.model_dump(mode="json"),
                )
                db.add(orm_obj)
                db.commit()
        except Exception as e:
            logger.debug(f"DB event insert skipped or failed: {e}")

    def _persist_behaviour_metric(self, model: BehaviourAnalysisModel):
        try:
            with SessionLocal() as db:
                orm_obj = BehaviourMetricORM(
                    analysis_id=model.analysis_id or f"BA-{model.operator_id}",
                    operator_id=model.operator_id,
                    machine_id=model.machine_id,
                    timestamp=model.timestamp,
                    excessive_idling_score=model.excessive_idling_score,
                    aggressive_maneuver_count=model.aggressive_maneuver_count,
                    unsafe_speed_events=model.unsafe_speed_events,
                    cycle_consistency_pct=model.cycle_consistency_pct,
                    overall_behaviour_score=model.overall_behaviour_score,
                    flags=model.flags,
                    anomaly_detected=model.anomaly_detected,
                    anomaly_score=model.anomaly_score,
                    constraint_flags=model.constraint_flags or [],
                )
                db.add(orm_obj)
                db.commit()
        except Exception as e:
            logger.debug(f"DB behaviour metric insert skipped or failed: {e}")


# Singleton instance
safety_service = SafetyService()
