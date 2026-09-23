"""
Operational Prediction Proxies for CAT Trajectory.
Estimates fuel consumption proxy (fuel_litres), idle impact (idle_minutes),
and productivity output proxy (productive_output_proxy, tons_per_hour, pace_pct).

Adheres to core product positioning: These are transparent engineering proxies
supporting scenario consequence evaluation, NOT certified fuel economics.
"""

from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge


class OperationalProxyEngine:
    """Predictive and physics-grounded proxy engine for operational multi-order effects."""

    def __init__(self):
        # Fuel consumption regressor
        self.fuel_model = Ridge(alpha=1.0)
        # Idle minutes regressor
        self.idle_model = Ridge(alpha=1.0)
        self.is_fitted: bool = False

    def fit(self, X_features: np.ndarray, df_train: pd.DataFrame):
        """Fits proxy models on training feature vectors and targets."""
        fuel_target = df_train["fuel_litres"].values
        idle_target = df_train["idle_minutes"].values

        self.fuel_model.fit(X_features, fuel_target)
        self.idle_model.fit(X_features, idle_target)
        self.is_fitted = True
        return self

    def estimate_fuel_litres(
        self,
        features: np.ndarray,
        machine_model: str = "CAT-349D",
        engine_load_pct: float = 72.0,
        active_hours: float = 2.5,
        idle_hours: float = 0.5
    ) -> float:
        """Estimates fuel consumption proxy in litres."""
        if self.is_fitted and features is not None:
            if len(features.shape) == 1:
                feat = features.reshape(1, -1)
            else:
                feat = features
            pred = float(self.fuel_model.predict(feat)[0])
            return float(round(max(5.0, pred), 1))

        # Fallback physics calculation calibrated to CAT 349D / D8T specs
        active_burn_rate = 36.0 * (engine_load_pct / 75.0) if "349" in machine_model else 26.0 * (engine_load_pct / 75.0)
        idle_burn_rate = 13.5
        calculated = (active_hours * active_burn_rate) + (idle_hours * idle_burn_rate)
        return float(round(calculated, 1))

    def estimate_idle_minutes(
        self,
        features: np.ndarray,
        queue_length: int = 1,
        truck_arrival_interval: float = 6.0,
        duration_minutes: float = 180.0
    ) -> float:
        """Estimates idle minutes proxy based on queue pressure and duration."""
        if self.is_fitted and features is not None:
            if len(features.shape) == 1:
                feat = features.reshape(1, -1)
            else:
                feat = features
            pred = float(self.idle_model.predict(feat)[0])
            return float(round(max(0.0, pred), 1))

        # Fallback physics calculation
        base_idle = duration_minutes * 0.08
        queue_idle = max(0, queue_length - 1) * (truck_arrival_interval * 0.6)
        return float(round(base_idle + queue_idle, 1))

    def estimate_productivity(
        self,
        target_volume_tons: float,
        duration_minutes: float,
        cycle_time_sec: float = 28.0,
        payload_tons: float = 24.0,
        idle_minutes: float = 15.0
    ) -> Dict[str, Any]:
        """Calculates productive output proxy metrics."""
        active_minutes = max(5.0, duration_minutes - idle_minutes)
        cycles_completed = (active_minutes * 60.0) / max(10.0, cycle_time_sec)
        estimated_volume_tons = float(round(cycles_completed * payload_tons, 1))

        hours = max(0.1, duration_minutes / 60.0)
        tons_per_hour = float(round(estimated_volume_tons / hours, 1))
        pace_pct = float(round((estimated_volume_tons / max(1.0, target_volume_tons)) * 100.0, 1))

        if pace_pct >= 105.0:
            rating = "OPTIMAL"
        elif pace_pct >= 95.0:
            rating = "HIGH"
        elif pace_pct >= 80.0:
            rating = "MODERATE"
        else:
            rating = "DEGRADED"

        return {
            "productive_output_proxy": estimated_volume_tons,
            "tons_per_hour": tons_per_hour,
            "pace_percentage": pace_pct,
            "efficiency_rating": rating,
        }
