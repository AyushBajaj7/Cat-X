"""Incident lifecycle and deduplication management."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ..config import settings
from ..database import SessionLocal
from ..db_models import SafetyIncidentORM
from ..models import (
    AlertSeverity,
    IncidentModel,
    IncidentStatus,
)

logger = logging.getLogger("safety.incidents")


class IncidentManager:
    """
    Manages safety incident creation, deduplication across time windows,
    and state transitions (OPEN -> ACKNOWLEDGED -> RESOLVED).
    """

    def __init__(self):
        # In-memory store: incident_id -> IncidentModel
        self._incidents: Dict[str, IncidentModel] = {}
        # Deduplication tracker: (operator_id, machine_id, incident_type) -> last_timestamp
        self._dedup_cache: Dict[tuple[str, str, str], datetime] = {}

    def log_incident(
        self,
        operator_id: str,
        machine_id: str,
        incident_type: str,
        severity: AlertSeverity,
        description: str,
        task_id: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        logged_by: str = "SYSTEM_AUTOMATED",
    ) -> Optional[IncidentModel]:
        """
        Record a safety incident with automatic deduplication.
        Returns the new incident if logged, or None if deduplicated.
        """
        now = datetime.now(timezone.utc)
        dedup_key = (operator_id, machine_id, incident_type)

        if dedup_key in self._dedup_cache:
            last_time = self._dedup_cache[dedup_key]
            elapsed_sec = (now - last_time).total_seconds()
            if elapsed_sec < settings.incident_dedup_window_seconds:
                logger.info(
                    f"Deduplicated incident {incident_type} for {operator_id} (elapsed: {elapsed_sec:.1f}s < {settings.incident_dedup_window_seconds}s)"
                )
                return None

        # Generate unique incident ID
        ts_ms = int(now.timestamp() * 1000)
        incident_id = f"INC-{operator_id}-{ts_ms}"

        incident = IncidentModel(
            incident_id=incident_id,
            timestamp=now,
            operator_id=operator_id,
            machine_id=machine_id,
            task_id=task_id,
            incident_type=incident_type,
            severity=severity,
            description=description,
            logged_by=logged_by,
            status=IncidentStatus.OPEN,
            evidence=evidence,
        )

        # Store in-memory and update dedup cache
        self._incidents[incident_id] = incident
        self._dedup_cache[dedup_key] = now

        # Persist to database if available
        self._persist_to_db(incident)

        return incident

    def acknowledge_incident(
        self, incident_id: str, acknowledged_by: str = "SUPERVISOR_CONSOLE"
    ) -> Optional[IncidentModel]:
        """Transition incident from OPEN to ACKNOWLEDGED."""
        incident = self._incidents.get(incident_id)
        if not incident:
            incident = self._load_from_db(incident_id)

        if not incident:
            return None

        now = datetime.now(timezone.utc)
        incident.status = IncidentStatus.ACKNOWLEDGED
        incident.acknowledged_at = now
        incident.acknowledged_by = acknowledged_by
        self._incidents[incident_id] = incident

        # Update DB
        self._update_db_status(incident)
        return incident

    def resolve_incident(
        self,
        incident_id: str,
        resolved_by: str = "SUPERVISOR_CONSOLE",
        resolution_notes: str = "",
    ) -> Optional[IncidentModel]:
        """Transition incident from OPEN/ACKNOWLEDGED to RESOLVED."""
        incident = self._incidents.get(incident_id)
        if not incident:
            incident = self._load_from_db(incident_id)

        if not incident:
            return None

        now = datetime.now(timezone.utc)
        incident.status = IncidentStatus.RESOLVED
        incident.resolved_at = now
        incident.resolved_by = resolved_by
        incident.resolution_notes = resolution_notes
        self._incidents[incident_id] = incident

        # Update DB
        self._update_db_status(incident)
        return incident

    def get_incidents(
        self,
        operator_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[IncidentModel]:
        """Retrieve incidents matching filter criteria."""
        results: List[IncidentModel] = []

        # First check in-memory store
        for inc in self._incidents.values():
            if operator_id and inc.operator_id != operator_id:
                continue
            if status and inc.status.value != status:
                continue
            results.append(inc)

        # If in-memory is empty, try database
        if not results:
            db_results = self._query_db(operator_id, status, limit)
            if db_results:
                return db_results

        # Return sorted by timestamp descending
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]

    def _persist_to_db(self, incident: IncidentModel) -> None:
        try:
            with SessionLocal() as db:
                orm_obj = SafetyIncidentORM(
                    incident_id=incident.incident_id,
                    timestamp=incident.timestamp,
                    operator_id=incident.operator_id,
                    machine_id=incident.machine_id,
                    task_id=incident.task_id,
                    incident_type=incident.incident_type,
                    severity=incident.severity.value,
                    description=incident.description,
                    logged_by=incident.logged_by,
                    status=incident.status.value,
                    evidence=incident.evidence,
                )
                db.add(orm_obj)
                db.commit()
        except Exception as e:
            logger.debug(f"DB incident insert skipped or failed: {e}")

    def _update_db_status(self, incident: IncidentModel) -> None:
        try:
            with SessionLocal() as db:
                orm_obj = (
                    db.query(SafetyIncidentORM)
                    .filter(SafetyIncidentORM.incident_id == incident.incident_id)
                    .first()
                )
                if orm_obj:
                    orm_obj.status = incident.status.value
                    orm_obj.acknowledged_at = incident.acknowledged_at
                    orm_obj.acknowledged_by = incident.acknowledged_by
                    orm_obj.resolved_at = incident.resolved_at
                    orm_obj.resolved_by = incident.resolved_by
                    orm_obj.resolution_notes = incident.resolution_notes
                    db.commit()
        except Exception as e:
            logger.debug(f"DB incident status update skipped or failed: {e}")

    def _load_from_db(self, incident_id: str) -> Optional[IncidentModel]:
        try:
            with SessionLocal() as db:
                orm_obj = (
                    db.query(SafetyIncidentORM)
                    .filter(SafetyIncidentORM.incident_id == incident_id)
                    .first()
                )
                if orm_obj:
                    return IncidentModel(
                        incident_id=orm_obj.incident_id,
                        timestamp=orm_obj.timestamp,
                        operator_id=orm_obj.operator_id,
                        machine_id=orm_obj.machine_id,
                        task_id=orm_obj.task_id,
                        incident_type=orm_obj.incident_type,
                        severity=AlertSeverity(orm_obj.severity),
                        description=orm_obj.description,
                        logged_by=orm_obj.logged_by,
                        status=IncidentStatus(orm_obj.status),
                        acknowledged_at=orm_obj.acknowledged_at,
                        acknowledged_by=orm_obj.acknowledged_by,
                        resolved_at=orm_obj.resolved_at,
                        resolved_by=orm_obj.resolved_by,
                        resolution_notes=orm_obj.resolution_notes,
                        evidence=orm_obj.evidence,
                    )
        except Exception as e:
            logger.debug(f"DB incident load skipped or failed: {e}")
        return None

    def _query_db(
        self,
        operator_id: Optional[str],
        status: Optional[str],
        limit: int,
    ) -> List[IncidentModel]:
        try:
            with SessionLocal() as db:
                q = db.query(SafetyIncidentORM)
                if operator_id:
                    q = q.filter(SafetyIncidentORM.operator_id == operator_id)
                if status:
                    q = q.filter(SafetyIncidentORM.status == status)
                q = q.order_by(SafetyIncidentORM.timestamp.desc()).limit(limit)
                rows = q.all()
                return [
                    IncidentModel(
                        incident_id=r.incident_id,
                        timestamp=r.timestamp,
                        operator_id=r.operator_id,
                        machine_id=r.machine_id,
                        task_id=r.task_id,
                        incident_type=r.incident_type,
                        severity=AlertSeverity(r.severity),
                        description=r.description,
                        logged_by=r.logged_by,
                        status=IncidentStatus(r.status),
                        acknowledged_at=r.acknowledged_at,
                        acknowledged_by=r.acknowledged_by,
                        resolved_at=r.resolved_at,
                        resolved_by=r.resolved_by,
                        resolution_notes=r.resolution_notes,
                        evidence=r.evidence,
                    )
                    for r in rows
                ]
        except Exception as e:
            logger.debug(f"DB incident query skipped or failed: {e}")
            return []
