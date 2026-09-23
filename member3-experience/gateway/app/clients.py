"""Asynchronous HTTP clients communicating with downstream services."""

from typing import Any, Dict, List
import httpx
from .config import settings
from .demo import demo_engine


class ServiceClients:
    """Async HTTP client facade for communicating with Safety, Operations, and Training services."""

    def __init__(self):
        self.timeout = 1.0 if getattr(settings, "environment", "") == "test" else 1.5

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
        """Fan out telemetry event to safety and operations services."""
        results: Dict[str, Any] = {}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for name, url in [
                ("safety", f"{settings.safety_service_url}/api/v1/safety/telemetry"),
                ("operations", f"{settings.operations_service_url}/api/v1/telemetry"),
            ]:
                try:
                    resp = await client.post(url, json=telemetry, timeout=3.0)
                    results[name] = resp.json() if resp.status_code in (200, 202) else {"status": "ERROR", "code": resp.status_code}
                except Exception:
                    results[name] = {"status": "UNAVAILABLE"}
        return {"event_id": telemetry.get("event_id", ""), "fanout": results}

    async def get_safety_status(self, operator_id: str) -> Dict[str, Any]:
        """Fetch safety status from the safety service, or demo state if offline."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.safety_service_url}/api/v1/safety/status/{operator_id}")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        # Fallback to demo state for operator
        demo_info = demo_engine.get_current_state()
        return {
            "operator_id": operator_id,
            "machine_id": demo_engine.machine_id,
            "timestamp": demo_info["timestamp"],
            "seatbelt_fastened": demo_info["seatbelt_fastened"],
            "seatbelt_compliance_pct": 72.0 if not demo_info["seatbelt_fastened"] else 99.4,
            "proximity_warning_level": "HIGH" if demo_info["active_hazard_count"] > 0 else "NONE",
            "active_hazard_count": demo_info["active_hazard_count"],
            "overall_safety_score": demo_info["safety_score"],
        }

    async def get_shift_twin(self, operator_id: str) -> Dict[str, Any]:
        """Fetch canonical Shift Twin from operations service, or demo state if offline."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.operations_service_url}/api/v1/operator/{operator_id}/shift-twin")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return demo_engine.get_shift_twin(operator_id)

    async def get_training_modules(self) -> List[Dict[str, Any]]:
        """Query the training service module catalog."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.training_service_url}/api/v1/training/modules")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return [
            {
                "module_id": "SAFE_START_01",
                "title": "Safe Start Check",
                "description": "Identify startup conditions, confirm safety context, confirm seatbelt, check operating environment, make safe decision.",
                "objective": "Confirm a safe operating context before beginning the task.",
                "difficulty": "BEGINNER",
                "estimated_minutes": 8,
                "skills": ["safety checks", "seatbelt compliance", "site awareness"],
                "steps": [
                    "Identify startup conditions.",
                    "Confirm safety context.",
                    "Confirm seatbelt is secure.",
                    "Check operating environment.",
                    "Make the safe decision before moving."
                ],
            },
            {
                "module_id": "PROXIMITY_RESPONSE_01",
                "title": "Proximity Response",
                "description": "Identify hazard, assess situation, choose appropriate response.",
                "objective": "Identify a proximity hazard and choose the correct response.",
                "difficulty": "INTERMEDIATE",
                "estimated_minutes": 10,
                "skills": ["hazard recognition", "situational awareness", "decision-making"],
                "steps": [
                    "Identify the hazard.",
                    "Assess the changing situation.",
                    "Choose an appropriate response.",
                    "Confirm the safe operating path."
                ],
            },
            {
                "module_id": "IDLE_EFFICIENCY_01",
                "title": "Idle Efficiency Response",
                "description": "Identify inefficient idle, choose appropriate operational response.",
                "objective": "Reduce inefficient idle and restore productive operation.",
                "difficulty": "INTERMEDIATE",
                "estimated_minutes": 12,
                "skills": ["fuel management", "idle reduction", "operational flow"],
                "steps": [
                    "Identify the inefficient idle condition.",
                    "Choose the appropriate operational response.",
                    "Reduce wasted time and fuel.",
                    "Resume productive workflow."
                ],
            },
            {
                "module_id": "DECISION_AWARENESS_01",
                "title": "Decision Awareness",
                "description": "Present a simplified operational decision, show alternatives, ask operator to select, show consequences.",
                "objective": "Understand the link between operator decisions and operational consequences.",
                "difficulty": "ADVANCED",
                "estimated_minutes": 14,
                "skills": ["trajectory comparison", "consequence reading", "decision trace"],
                "steps": [
                    "Present a simplified operational decision.",
                    "Show trajectories or alternatives.",
                    "Ask the operator to select a path.",
                    "Show expected consequences.",
                    "Connect the decision to the shift outcome."
                ],
            },
        ]

    async def get_training_module(self, module_id: str) -> Dict[str, Any]:
        """Query one training module."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.training_service_url}/api/v1/training/modules/{module_id}")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        module = next((m for m in await self.get_training_modules() if m.get("module_id") == module_id), None)
        if module is not None:
            return module
        raise KeyError(f"Module {module_id} not found")

    async def get_training_recommendations(self, operator_id: str, signal: str = None) -> List[Dict[str, Any]]:
        """Fetch personalized recommendations from the training service."""
        url = f"{settings.training_service_url}/api/v1/training/recommendations/{operator_id}"
        if signal:
            url += f"?signal={signal}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        # Fallback: when training service is offline, use signal-to-module mapping
        demo_info = demo_engine.get_current_state()
        signal_map = {
            "seatbelt": ("SAFE_START_01", "Safe Start Check", "Seatbelt non-compliance detected. Review safe operating procedures.", "HIGH"),
            "proximity": ("PROXIMITY_RESPONSE_01", "Proximity Response", "Proximity boundary alert triggered. Review hazard response guidelines.", "HIGH"),
            "idle": ("IDLE_EFFICIENCY_01", "Idle Efficiency Response", "Excessive low-idle operation observed. Review engine power management.", "MEDIUM"),
            "high idle": ("IDLE_EFFICIENCY_01", "Idle Efficiency Response", "Excessive low-idle operation observed. Review engine power management.", "MEDIUM"),
            "decision": ("DECISION_AWARENESS_01", "Decision Awareness", "Emergent tactical decision point encountered. Review consequence graphs.", "MEDIUM"),
        }
        if signal:
            normalized = signal.lower().replace("_", " ")
            for key, (mod_id, mod_title, reason, urgency) in signal_map.items():
                if key in normalized:
                    return [{
                        "recommendation_id": f"REC-{operator_id}-{mod_id}",
                        "operator_id": operator_id,
                        "module_id": mod_id,
                        "module_title": mod_title,
                        "urgency": urgency,
                        "trigger_source": "CONTEXT_SIGNAL",
                        "reason": reason,
                        "recommended_at": demo_info["timestamp"],
                    }]
        # No signal filter: return demo engine's top recommendation
        if demo_info.get("top_training_recommendation"):
            rec = demo_info["top_training_recommendation"]
            return [
                {
                    "recommendation_id": f"REC-{operator_id}-{rec['module_id']}",
                    "operator_id": operator_id,
                    "module_id": rec["module_id"],
                    "module_title": rec["module_title"],
                    "urgency": rec["urgency"],
                    "trigger_source": "CONTEXT_SIGNAL",
                    "reason": rec["reason"],
                    "recommended_at": demo_info["timestamp"],
                }
            ]
        return [
            {
                "recommendation_id": f"REC-{operator_id}-SAFE_START_01",
                "operator_id": operator_id,
                "module_id": "SAFE_START_01",
                "module_title": "Safe Start Check",
                "urgency": "MEDIUM",
                "trigger_source": "CONTEXT_SIGNAL",
                "reason": "Seatbelt non-compliance detected. Review safe operating procedures and startup sequence before continuing.",
                "recommended_at": "2026-09-23T07:30:00Z",
            }
        ]

    async def post_training_attempt(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a training attempt to the training service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{settings.training_service_url}/api/v1/training/attempts", json=payload)
                if resp.status_code == 201:
                    return resp.json()
            except Exception:
                pass
        max_score = float(payload.get("max_score", 100.0) or 100.0)
        score = float(payload.get("score", payload.get("score_pct", 85.0)) or 85.0)
        percentage = round((score / max_score) * 100.0, 2)
        return {
            "attempt_id": "ATT-DEMO-RECORDED",
            "operator_id": payload.get("operator_id", "OP1001"),
            "module_id": payload.get("module_id", "SAFE_START_01"),
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "mistakes": payload.get("mistakes", 0),
            "passed": percentage >= 80.0,
            "status": payload.get("status", "COMPLETED"),
            "completed_at": payload.get("completed_at") or "2026-09-23T07:35:00Z",
        }

    async def get_training_progress(self, operator_id: str) -> Dict[str, Any]:
        """Query training progress for an operator."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{settings.training_service_url}/api/v1/training/progress/{operator_id}")
                if resp.status_code == 200:
                    return resp.json()
            except Exception:
                pass
        return {
            "operator_id": operator_id,
            "completed_modules_count": 2,
            "average_score_pct": 91.5,
            "certifications_earned": ["CAT Level 1 Safety Basics", "Decision Awareness Fundamentals"],
            "last_activity_at": "2026-09-23T07:35:00Z",
        }


clients = ServiceClients()
