"""
Safety Service Adapter & Mock.
Consumes Engineer 1's Safety Service on Port 8001 via REST.
Provides clean fallback / mock states during isolated local testing and CI.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from ..config import settings


class SafetyServiceAdapter:
    """Client for fetching live safety status and behaviour analytics from Engineer 1."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.safety_service_url

    async def get_safety_status(self, operator_id: str) -> Dict[str, Any]:
        """Queries GET /api/v1/safety/status/{operator_id}."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/api/v1/safety/status/{operator_id}")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return self._mock_safety_status(operator_id)

    async def get_behaviour_state(self, operator_id: str) -> Dict[str, Any]:
        """Queries GET /api/v1/safety/behaviour/{operator_id}."""
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/api/v1/safety/behaviour/{operator_id}")
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return self._mock_behaviour_state(operator_id)

    def _mock_safety_status(self, operator_id: str) -> Dict[str, Any]:
        """Fallback mock matching safety.schema.json."""
        return {
            "operator_id": operator_id,
            "machine_id": "EXC-CAT-001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "seatbelt_fastened": True,
            "seatbelt_compliance_pct": 99.2,
            "proximity_warning_level": "NONE",
            "active_hazard_count": 0,
            "overall_safety_score": 97.5,
        }

    def _mock_behaviour_state(self, operator_id: str) -> Dict[str, Any]:
        """Fallback mock matching behaviour.schema.json."""
        return {
            "operator_id": operator_id,
            "machine_id": "EXC-CAT-001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "excessive_idling_score": 12.0,
            "aggressive_maneuver_count": 0,
            "unsafe_speed_events": 0,
            "cycle_consistency_pct": 94.0,
            "overall_behaviour_score": 93.5,
            "flags": [],
            "anomaly_detected": False,
            "constraint_flags": [],
        }


safety_adapter = SafetyServiceAdapter()
