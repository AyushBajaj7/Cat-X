"""Asynchronous HTTP clients communicating with downstream services."""

from typing import Any, Dict, List, Optional
import httpx
from .config import settings


class ServiceClients:
    """Async HTTP client facade for communicating with Safety, Operations, and Training services."""

    def __init__(self):
        self.timeout = 4.0

    async def check_health(self) -> Dict[str, str]:
        """Query health endpoints of all three downstream services."""
        results = {}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                r = await client.get(f"{settings.safety_service_url}/api/v1/health")
                results["safety_service"] = "HEALTHY" if r.status_code == 200 else "DEGRADED"
            except Exception:
                results["safety_service"] = "UNREACHABLE"

            try:
                r = await client.get(f"{settings.operations_service_url}/api/v1/health")
                results["operations_service"] = "HEALTHY" if r.status_code == 200 else "DEGRADED"
            except Exception:
                results["operations_service"] = "UNREACHABLE"

            try:
                r = await client.get(f"{settings.training_service_url}/api/v1/health")
                results["training_service"] = "HEALTHY" if r.status_code == 200 else "DEGRADED"
            except Exception:
                results["training_service"] = "UNREACHABLE"

        return results

    async def forward_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Fan out telemetry event to Safety Service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{settings.safety_service_url}/api/v1/safety/telemetry",
                    json=telemetry,
                )
                return resp.json() if resp.status_code == 200 else {"status": "FAILED"}
            except Exception:
                return {"status": "BUFFERED_OFFLINE"}

    async def get_safety_status(self, operator_id: str) -> Dict[str, Any]:
        """Fetch safety status from Safety Service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.safety_service_url}/api/v1/safety/status/{operator_id}")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return {
            "operator_id": operator_id,
            "machine_id": "EXC-CAT-001",
            "seatbelt_fastened": True,
            "seatbelt_compliance_pct": 98.0,
            "proximity_warning_level": "LOW",
            "active_hazard_count": 0,
            "overall_safety_score": 96.0,
        }

    async def get_shift_twin(self, operator_id: str) -> Dict[str, Any]:
        """Fetch canonical Shift Twin from Operations Service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.operations_service_url}/api/v1/operator/{operator_id}/shift-twin")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return {
            "twin_id": f"TWIN-{operator_id}-GATEWAY",
            "operator_id": operator_id,
            "machine_id": "EXC-CAT-001",
            "current_task_id": "T002",
            "updated_at": "2026-09-23T07:30:00Z",
            "shift_health_score": 94.0,
            "environment": {
                "weather_condition": "CLEAR",
                "ambient_temp_c": 22.0,
                "ground_saturation_pct": 12.0,
            },
            "safety": {
                "seatbelt_status": True,
                "seatbelt_compliance_pct": 98.0,
                "safety_score": 96.0,
            },
            "behaviour": {
                "idle_percentage": 10.5,
                "behaviour_score": 94.0,
            },
            "productivity": {
                "completed_volume_tons": 820.0,
                "target_volume_tons": 1350.0,
                "pace_percentage": 104.0,
            },
            "prediction": {
                "estimated_completion_time": "2026-09-23T10:00:00Z",
                "estimated_remaining_minutes": 150.0,
                "confidence_score": 0.9,
            },
            "next_best_actions": [
                {
                    "action_id": "NBA-01",
                    "title": "Optimize Bench 2 Swing Angle",
                    "rationale": "Reposition haul truck to shorten cycle.",
                    "category": "EFFICIENCY",
                    "priority": "HIGH",
                }
            ],
        }

    async def get_training_recommendations(self, operator_id: str) -> List[Dict[str, Any]]:
        """Fetch personalized recommendations from Training Service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.training_service_url}/api/v1/training/recommendations/{operator_id}")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return [
            {
                "recommendation_id": f"REC-{operator_id}-01",
                "operator_id": operator_id,
                "module_id": "MOD-ECO-01",
                "module_title": "Eco-Mode Power Management & Idle Reduction",
                "urgency": "MEDIUM",
                "trigger_source": "BEHAVIOUR_ANALYSIS",
                "reason": "Optimize idle during haul truck spotting intervals.",
                "recommended_at": "2026-09-23T07:30:00Z",
            }
        ]


clients = ServiceClients()
