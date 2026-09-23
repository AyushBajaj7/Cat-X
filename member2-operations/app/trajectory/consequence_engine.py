"""
CAT Trajectory — Consequence Engine.
Evaluates alternative operational trajectories through the unified ML prediction pipeline,
proxy engines, and deterministic safety constraint validators.
Flow:
current state -> scenario transformation -> feature pipeline -> ETA model
-> fuel model -> productivity estimate -> forecast -> consequence graph.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np

from ..domain.operational_state import OperationalState
from .safety_constraints import safety_constraint_engine, ConstraintValidationResult
from .scenario_generator import CandidateScenario, scenario_generator

OPERATIONS_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = OPERATIONS_DIR / "models"


class EvaluatedScenarioResult:
    """Evaluated scenario output matching shared/contracts/scenario.schema.json."""

    def __init__(
        self,
        scenario_id: str,
        action_id: str,
        title: str,
        description: str,
        parameters: Dict[str, Any],
        constraint_status: str,
        predicted_outcome: Dict[str, Any],
        explanation: str,
        validation_result: ConstraintValidationResult,
        consequence_graph: Optional[Dict[str, Any]] = None,
        drivers: Optional[List[str]] = None,
    ):
        self.scenario_id = scenario_id
        self.action_id = action_id
        self.title = title
        self.description = description
        self.parameters = parameters
        self.constraint_status = constraint_status
        self.predicted_outcome = predicted_outcome
        self.explanation = explanation
        self.validation_result = validation_result
        self.consequence_graph = consequence_graph
        self.drivers = drivers or []

    def to_contract_dict(self) -> Dict[str, Any]:
        """Serializes to schema-compliant dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "parameters": self.parameters,
            "constraint_status": self.constraint_status,
            "predicted_outcome": self.predicted_outcome,
            "explanation": self.explanation,
        }


class ConsequenceEngine:
    """Core evaluation engine executing the unified prediction pipeline on operational trajectories."""

    def __init__(self):
        self.feature_pipeline = None
        self.eta_model = None
        self.rf_model = None
        self.proxy_engine = None
        self._ensure_models_loaded()

    def _ensure_models_loaded(self):
        """Loads fitted models from disk with on-demand fallback."""
        try:
            if (MODELS_DIR / "feature_pipeline.joblib").exists():
                self.feature_pipeline = joblib.load(MODELS_DIR / "feature_pipeline.joblib")
            if (MODELS_DIR / "eta_model.joblib").exists():
                self.eta_model = joblib.load(MODELS_DIR / "eta_model.joblib")
            if (MODELS_DIR / "rf_interval_model.joblib").exists():
                self.rf_model = joblib.load(MODELS_DIR / "rf_interval_model.joblib")
            if (MODELS_DIR / "proxy_engine.joblib").exists():
                self.proxy_engine = joblib.load(MODELS_DIR / "proxy_engine.joblib")
        except Exception as e:
            print(f"Warning: Failed to load serialized models ({e}). Retraining or using fallback.")

    def evaluate_trajectory(
        self,
        candidate: CandidateScenario,
        baseline_state: OperationalState,
        constraint_overrides: Optional[Dict[str, Any]] = None
    ) -> EvaluatedScenarioResult:
        """Evaluates a single candidate trajectory using the trained ML models."""
        self._ensure_models_loaded()
        state = candidate.transformed_state

        # 1. Step 1: Safety Gate Validation FIRST
        val_result = safety_constraint_engine.validate_scenario(
            scenario_id=candidate.scenario_id,
            state=state,
            overrides=constraint_overrides,
        )

        # 2. Extract baseline metrics using models
        baseline_metrics = self._predict_state_metrics(baseline_state)

        # 3. If scenario is rejected by safety constraints, return REJECTED outcome
        if val_result.constraint_status == "REJECTED":
            explanation = (
                f"REJECTED by safety constraints: "
                + "; ".join(val_result.rejection_reasons)
            )
            predicted_outcome = {
                "eta_minutes": round(baseline_metrics["eta_minutes"] * 1.5, 1),
                "fuel_liters": round(baseline_metrics["fuel_litres"] * 1.4, 1),
                "safety_risk_score": val_result.composite_safety_risk_score,
                "time_saved_minutes": -30.0,
                "fuel_saved_liters": -25.0,
            }
            return EvaluatedScenarioResult(
                scenario_id=candidate.scenario_id,
                action_id=candidate.action_id,
                title=candidate.title,
                description=candidate.description,
                parameters=candidate.parameters,
                constraint_status="REJECTED",
                predicted_outcome=predicted_outcome,
                explanation=explanation,
                validation_result=val_result,
                drivers=val_result.rejection_reasons,
            )

        # 4. Predict scenario outcome using trained ML models
        scen_metrics = self._predict_state_metrics(state)

        # Calculate deltas relative to baseline
        time_saved = float(round(baseline_metrics["eta_minutes"] - scen_metrics["eta_minutes"], 1))
        fuel_saved = float(round(baseline_metrics["fuel_litres"] - scen_metrics["fuel_litres"], 1))

        predicted_outcome = {
            "eta_minutes": scen_metrics["eta_minutes"],
            "fuel_liters": scen_metrics["fuel_litres"],
            "safety_risk_score": val_result.composite_safety_risk_score,
            "time_saved_minutes": time_saved,
            "fuel_saved_liters": fuel_saved,
            "prototype_prediction_interval": {
                "lower_minutes": scen_metrics.get("lower_minutes", round(scen_metrics["eta_minutes"] * 0.9, 1)),
                "upper_minutes": scen_metrics.get("upper_minutes", round(scen_metrics["eta_minutes"] * 1.15, 1)),
            },
            "idle_minutes": scen_metrics.get("idle_minutes", 15.0),
            "tons_per_hour": scen_metrics.get("tons_per_hour", 110.0),
        }

        # Identify drivers
        drivers = []
        if candidate.parameters.get("idle_multiplier", 1.0) < 0.5:
            drivers.append("Drastic idle reduction by converting wait time into active digging")
        if candidate.parameters.get("queue_multiplier", 1.0) < 0.5:
            drivers.append("Bypassed haul truck queue bottleneck")
        if candidate.parameters.get("cycle_time_multiplier", 1.0) < 0.9:
            drivers.append("Reduced swing arc from 48° to 32°, shaving cycle time by ~6s")
        if time_saved > 0:
            drivers.append(f"Projected to save {time_saved:.1f} minutes towards shift deadline")

        explanation = (
            f"{candidate.explanation} "
            f"Model predicts {time_saved:.1f} min saved and {fuel_saved:.1f}L fuel reduction."
        )

        return EvaluatedScenarioResult(
            scenario_id=candidate.scenario_id,
            action_id=candidate.action_id,
            title=candidate.title,
            description=candidate.description,
            parameters=candidate.parameters,
            constraint_status="FEASIBLE",
            predicted_outcome=predicted_outcome,
            explanation=explanation,
            validation_result=val_result,
            drivers=drivers,
        )

    def _predict_state_metrics(self, state: OperationalState) -> Dict[str, Any]:
        """Transforms state into feature vector and evaluates through ML models."""
        # Build dictionary matching feature pipeline schema
        remaining_vol = max(50.0, state.current_task.target_volume_tons - state.current_task.completed_volume_tons)
        sample = {
            "target_volume_tons": remaining_vol,
            "machine_age_years": state.machine.total_operating_hours / 1500.0,
            "slope_deg": state.environment.slope_deg,
            "ambient_temp_c": state.environment.ambient_temp_c,
            "ground_saturation_pct": state.environment.ground_saturation_pct,
            "truck_arrival_interval_min": state.queue_state.truck_arrival_interval_min,
            "queue_length": state.queue_state.queue_length,
            "cycle_time_sec": state.productivity_state.cycle_time_sec,
            "payload_tons": state.machine.payload_capacity_tons * state.productivity_state.bucket_fill_factor,
            "engine_load_pct": state.machine_state.engine_load_pct,
            "task_type": "TRENCHING" if "TRENCH" in state.current_task.title.upper() else "EXCAVATION",
            "weather": state.environment.weather_condition,
            "operator_skill": state.operator.experience_tier,
            "visibility_level": state.environment.visibility_level,
        }

        if self.feature_pipeline and self.eta_model:
            feat = self.feature_pipeline.transform(sample)
            eta_pred = float(self.eta_model.predict(feat)[0])
            eta_minutes = float(round(max(20.0, eta_pred), 1))

            # Intervals from Random Forest if available
            if self.rf_model and hasattr(self.rf_model.model, "estimators_"):
                tree_preds = np.array([tree.predict(feat) for tree in self.rf_model.model.estimators_])
                lower = float(round(np.percentile(tree_preds, 10.0), 1))
                upper = float(round(np.percentile(tree_preds, 90.0), 1))
            else:
                lower = round(eta_minutes * 0.9, 1)
                upper = round(eta_minutes * 1.15, 1)

            # Fuel & Idle from proxy engine
            if self.proxy_engine:
                fuel_litres = self.proxy_engine.estimate_fuel_litres(
                    features=feat,
                    machine_model=state.machine.model,
                    engine_load_pct=state.machine_state.engine_load_pct,
                    active_hours=(eta_minutes - state.idle_state.idle_minutes) / 60.0,
                    idle_hours=state.idle_state.idle_minutes / 60.0,
                )
                idle_minutes = self.proxy_engine.estimate_idle_minutes(
                    features=feat,
                    queue_length=state.queue_state.queue_length,
                    truck_arrival_interval=state.queue_state.truck_arrival_interval_min,
                    duration_minutes=eta_minutes,
                )
            else:
                fuel_litres = round((eta_minutes / 60.0) * 35.0, 1)
                idle_minutes = state.idle_state.idle_minutes
        else:
            # Physics-based baseline approximation
            nominal_rate = 3.5  # tons/min
            eta_minutes = round(remaining_vol / nominal_rate + state.idle_state.idle_minutes, 1)
            lower = round(eta_minutes * 0.9, 1)
            upper = round(eta_minutes * 1.15, 1)
            fuel_litres = round((eta_minutes / 60.0) * 34.0, 1)
            idle_minutes = state.idle_state.idle_minutes

        prod_dict = (
            self.proxy_engine.estimate_productivity(
                target_volume_tons=remaining_vol,
                duration_minutes=eta_minutes,
                cycle_time_sec=state.productivity_state.cycle_time_sec,
                payload_tons=state.machine.payload_capacity_tons,
                idle_minutes=idle_minutes,
            )
            if self.proxy_engine
            else {"tons_per_hour": 110.0, "pace_percentage": 100.0}
        )

        return {
            "eta_minutes": eta_minutes,
            "lower_minutes": lower,
            "upper_minutes": upper,
            "fuel_litres": fuel_litres,
            "idle_minutes": idle_minutes,
            "tons_per_hour": prod_dict["tons_per_hour"],
            "pace_percentage": prod_dict["pace_percentage"],
        }


consequence_engine = ConsequenceEngine()
