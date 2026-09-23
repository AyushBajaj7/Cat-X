"""
Shared Feature Engineering Pipeline for Operations & CAT Trajectory.
Ensures zero training/serving mismatch across training, validation, real-time prediction,
and counterfactual scenario evaluation.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

FEATURE_NAMES = [
    "target_volume_tons",
    "machine_age_years",
    "slope_deg",
    "ambient_temp_c",
    "ground_saturation_pct",
    "truck_arrival_interval_min",
    "queue_length",
    "cycle_time_sec",
    "payload_tons",
    "engine_load_pct",
    "cycles_per_hour",
    "queue_pressure",
    "task_type_EXCAVATION",
    "task_type_GRADING",
    "task_type_LOADING",
    "task_type_OVERBURDEN",
    "task_type_TRENCHING",
    "weather_CLEAR",
    "weather_FOG",
    "weather_MUD",
    "weather_OVERCAST",
    "weather_RAIN",
    "skill_level_score",
    "visibility_score",
]

SKILL_MAP = {"NOVICE": 1.0, "INTERMEDIATE": 2.0, "EXPERT": 3.0, "MASTER": 4.0}
VISIBILITY_MAP = {"POOR": 1.0, "MODERATE": 2.0, "GOOD": 3.0, "EXCELLENT": 4.0}
TASK_TYPES = ["EXCAVATION", "GRADING", "LOADING", "OVERBURDEN", "TRENCHING"]
WEATHERS = ["CLEAR", "FOG", "MUD", "OVERCAST", "RAIN"]


class OperationalFeaturePipeline(BaseEstimator, TransformerMixin):
    """Unified transformer for converting operational state or task records into ML features."""

    def __init__(self):
        self.feature_names: List[str] = FEATURE_NAMES
        self.is_fitted: bool = False
        self.medians_: Dict[str, float] = {}

    def fit(self, X: Union[pd.DataFrame, List[Dict[str, Any]]], y=None):
        """Fits baseline imputation medians from training distribution."""
        if isinstance(X, list):
            df = pd.DataFrame(X)
        else:
            df = X.copy()

        numeric_cols = [
            "target_volume_tons",
            "machine_age_years",
            "slope_deg",
            "ambient_temp_c",
            "ground_saturation_pct",
            "truck_arrival_interval_min",
            "queue_length",
            "cycle_time_sec",
            "payload_tons",
            "engine_load_pct",
        ]
        for col in numeric_cols:
            if col in df.columns:
                self.medians_[col] = float(df[col].median())
            else:
                self.medians_[col] = 0.0

        self.is_fitted = True
        return self

    def transform(self, X: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """Transforms single dict or DataFrame into 2D numpy feature array."""
        if isinstance(X, dict):
            df = pd.DataFrame([X])
        elif isinstance(X, list):
            df = pd.DataFrame(X)
        else:
            df = X.copy()

        rows = []
        for _, row in df.iterrows():
            feat_dict = self._extract_row_features(row)
            row_vector = [feat_dict.get(k, 0.0) for k in self.feature_names]
            rows.append(row_vector)

        return np.array(rows, dtype=np.float64)

    def _extract_row_features(self, row: Any) -> Dict[str, float]:
        """Extracts engineered features for a single sample."""
        # Safe numeric getters with fitted medians as fallback
        target_volume = float(row.get("target_volume_tons", self.medians_.get("target_volume_tons", 600.0)))
        machine_age = float(row.get("machine_age_years", self.medians_.get("machine_age_years", 3.5)))
        slope = float(row.get("slope_deg", self.medians_.get("slope_deg", 4.0)))
        ambient_temp = float(row.get("ambient_temp_c", self.medians_.get("ambient_temp_c", 22.0)))
        saturation = float(row.get("ground_saturation_pct", self.medians_.get("ground_saturation_pct", 15.0)))
        arrival_interval = float(row.get("truck_arrival_interval_min", self.medians_.get("truck_arrival_interval_min", 6.0)))
        queue_len = float(row.get("queue_length", self.medians_.get("queue_length", 1.0)))
        cycle_time = float(row.get("cycle_time_sec", self.medians_.get("cycle_time_sec", 28.0)))
        payload = float(row.get("payload_tons", self.medians_.get("payload_tons", 24.0)))
        engine_load = float(row.get("engine_load_pct", self.medians_.get("engine_load_pct", 72.0)))

        # Engineered features
        cycles_per_hour = 3600.0 / max(10.0, cycle_time)
        queue_pressure = queue_len * arrival_interval

        # Categorical mappings
        task_type = str(row.get("task_type", "EXCAVATION")).upper()
        weather = str(row.get("weather", "CLEAR")).upper()
        skill = str(row.get("operator_skill", "INTERMEDIATE")).upper()
        vis = str(row.get("visibility_level", "GOOD")).upper()

        feat = {
            "target_volume_tons": target_volume,
            "machine_age_years": machine_age,
            "slope_deg": slope,
            "ambient_temp_c": ambient_temp,
            "ground_saturation_pct": saturation,
            "truck_arrival_interval_min": arrival_interval,
            "queue_length": queue_len,
            "cycle_time_sec": cycle_time,
            "payload_tons": payload,
            "engine_load_pct": engine_load,
            "cycles_per_hour": cycles_per_hour,
            "queue_pressure": queue_pressure,
            "skill_level_score": SKILL_MAP.get(skill, 2.0),
            "visibility_score": VISIBILITY_MAP.get(vis, 3.0),
        }

        # One-hot task types
        for t in TASK_TYPES:
            feat[f"task_type_{t}"] = 1.0 if task_type == t else 0.0

        # One-hot weather
        for w in WEATHERS:
            feat[f"weather_{w}"] = 1.0 if weather == w else 0.0

        return feat
