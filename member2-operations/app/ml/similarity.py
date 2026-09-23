"""
Operational Context Similarity Engine.
Uses scikit-learn StandardScaler and NearestNeighbors (no vector DB)
to index and retrieve historical benchmark shifts and past decision memories.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

SIMILARITY_FEATURE_COLS = [
    "machine_age_years",
    "ambient_temp_c",
    "ground_saturation_pct",
    "slope_deg",
    "truck_arrival_interval_min",
    "queue_length",
    "cycle_time_sec",
    "payload_tons",
    "engine_load_pct",
    "idle_minutes",
    "task_duration_minutes",
]

TASK_MAP = {"EXCAVATION": 1.0, "TRENCHING": 2.0, "LOADING": 3.0, "GRADING": 4.0, "OVERBURDEN": 5.0}
WEATHER_MAP = {"CLEAR": 1.0, "OVERCAST": 2.0, "RAIN": 3.0, "MUD": 4.0, "FOG": 5.0}
SKILL_MAP = {"NOVICE": 1.0, "INTERMEDIATE": 2.0, "EXPERT": 3.0, "MASTER": 4.0}


class ContextSimilarityEngine:
    """NearestNeighbors context matcher for historical shifts and operational decisions."""

    def __init__(self, n_neighbors: int = 5):
        self.scaler = StandardScaler()
        self.nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
        self.indexed_records: List[Dict[str, Any]] = []
        self.is_fitted: bool = False

    def _extract_context_vector(self, record: Dict[str, Any]) -> List[float]:
        """Extracts numerical vector representing operational context."""
        vec = [
            float(record.get("machine_age_years", 3.5)),
            float(record.get("ambient_temp_c", 22.0)),
            float(record.get("ground_saturation_pct", 15.0)),
            float(record.get("slope_deg", 4.0)),
            float(record.get("truck_arrival_interval_min", 6.0)),
            float(record.get("queue_length", 1.0)),
            float(record.get("cycle_time_sec", 28.0)),
            float(record.get("payload_tons", 24.0)),
            float(record.get("engine_load_pct", 72.0)),
            float(record.get("idle_minutes", 15.0)),
            float(record.get("task_duration_minutes", 180.0)),
            TASK_MAP.get(str(record.get("task_type", "EXCAVATION")).upper(), 1.0) * 10.0,
            WEATHER_MAP.get(str(record.get("weather", "CLEAR")).upper(), 1.0) * 10.0,
            SKILL_MAP.get(str(record.get("operator_skill", "INTERMEDIATE")).upper(), 2.0) * 10.0,
        ]
        return vec

    def fit(self, records: List[Dict[str, Any]]):
        """Indexes historical records into NearestNeighbors space."""
        if not records:
            raise ValueError("Cannot fit ContextSimilarityEngine on empty records.")

        self.indexed_records = list(records)
        vectors = np.array([self._extract_context_vector(r) for r in self.indexed_records], dtype=np.float64)
        scaled_vectors = self.scaler.fit_transform(vectors)
        self.nn_model.fit(scaled_vectors)
        self.is_fitted = True
        return self

    def find_similar(
        self,
        query_context: Dict[str, Any],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Finds top-k nearest historical contexts and computes similarity score percentages."""
        if not self.is_fitted or not self.indexed_records:
            return []

        query_vec = np.array([self._extract_context_vector(query_context)], dtype=np.float64)
        scaled_query = self.scaler.transform(query_vec)

        k = min(top_k, len(self.indexed_records))
        distances, indices = self.nn_model.kneighbors(scaled_query, n_neighbors=k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            rec = self.indexed_records[idx]
            # Convert Euclidean distance in scaled space to similarity percentage
            similarity_pct = float(round(max(50.0, min(99.5, 100.0 / (1.0 + (dist * 0.25)))), 1))
            res_item = dict(rec)
            res_item["similarity_score_pct"] = similarity_pct
            results.append(res_item)

        return results

    def compute_context_signature(self, record: Dict[str, Any]) -> str:
        """Produces a deterministic human-readable context signature hash."""
        task = str(record.get("task_type", "EXCAVATION")).upper()
        weather = str(record.get("weather", "CLEAR")).upper()
        skill = str(record.get("operator_skill", "INTERMEDIATE")).upper()
        queue = int(record.get("queue_length", 1))
        queue_label = "HIQUEUE" if queue >= 3 else "NORMQUEUE"
        return f"SIG-{task}-{weather}-{skill}-{queue_label}"
