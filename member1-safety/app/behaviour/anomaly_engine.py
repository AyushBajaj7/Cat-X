"""Multivariate anomaly detection engine using scikit-learn IsolationForest.

NOTE: The anomaly score is a normalized [0, 1] index of statistical deviation
from regular operating patterns. It must NOT be interpreted or described as
a 'probability of equipment failure'.
"""

from dataclasses import dataclass
import logging
from typing import Any, Dict, List
import numpy as np
from sklearn.ensemble import IsolationForest
from ..config import settings
from .features import BehaviourFeatures

logger = logging.getLogger("safety.anomaly")


@dataclass
class AnomalyDetectionResult:
    """Outcome of multivariate operational anomaly evaluation."""

    anomaly_detected: bool
    anomaly_score: float  # [0.0, 1.0]
    decision_function_score: float
    contributing_features: List[str]
    evidence: Dict[str, Any]


class AnomalyEngine:
    """
    Evaluates multivariate behavioral telemetry feature vectors against an
    ensemble Isolation Forest model.
    """

    def __init__(self):
        self.model = IsolationForest(
            n_estimators=settings.isolation_forest_n_estimators,
            contamination=settings.isolation_forest_contamination,
            random_state=settings.isolation_forest_random_state,
            n_jobs=1,
        )
        self._is_fitted = False
        self._fit_default_reference_distribution()

    def _fit_default_reference_distribution(self):
        """Fit model with reference synthetic nominal operational distributions."""
        rng = np.random.default_rng(42)
        n_samples = 120

        # Generate realistic nominal features:
        # [mean_speed, max_speed, speed_var, mean_rpm, mean_fuel, idle_ratio,
        #  mean_fatigue, max_fatigue, compliance_pct, aggressive_count, unsafe_speed, consistency]
        speeds = rng.normal(1.6, 0.3, (n_samples, 1))
        max_speeds = speeds + rng.uniform(0.5, 1.5, (n_samples, 1))
        speed_vars = rng.uniform(0.2, 0.8, (n_samples, 1))
        rpms = rng.normal(1750.0, 100.0, (n_samples, 1))
        fuels = rng.normal(16.0, 2.0, (n_samples, 1))
        idles = rng.uniform(0.05, 0.20, (n_samples, 1))
        fatigues = rng.normal(25.0, 8.0, (n_samples, 1))
        max_fatigues = fatigues + rng.uniform(5.0, 12.0, (n_samples, 1))
        compliances = rng.uniform(95.0, 100.0, (n_samples, 1))
        aggressives = rng.poisson(0.1, (n_samples, 1))
        unsafes = rng.poisson(0.05, (n_samples, 1))
        consistencies = rng.normal(92.0, 3.0, (n_samples, 1))

        X_nominal = np.hstack([
            speeds,
            max_speeds,
            speed_vars,
            rpms,
            fuels,
            idles,
            fatigues,
            max_fatigues,
            compliances,
            aggressives,
            unsafes,
            consistencies,
        ])

        self.model.fit(X_nominal)
        self._is_fitted = True

    def score(self, features: BehaviourFeatures) -> AnomalyDetectionResult:
        """
        Score behavioral feature vector.
        Returns normalized anomaly score in [0.0, 1.0].
        """
        vec = np.array(features.to_feature_vector()).reshape(1, -1)
        raw_score = float(self.model.decision_function(vec)[0])
        pred = int(self.model.predict(vec)[0])  # 1: inlier, -1: outlier

        # Transform decision function to normalized [0, 1] range:
        # Lower decision function means higher outlierness.
        # Typically decision_function is in [-0.3, +0.3] for IsolationForest
        # We map it smoothly into [0.0, 1.0] using sigmoid-like scaling
        normalized_score = max(0.0, min(1.0, round(1.0 / (1.0 + np.exp(raw_score * 8.0)), 3)))

        anomaly_detected = (pred == -1) or (normalized_score >= 0.65)

        contributing = []
        if features.mean_fatigue > 60.0:
            contributing.append("HIGH_FATIGUE_EXPOSURE")
        if features.seatbelt_compliance_pct < 85.0:
            contributing.append("LOW_SEATBELT_COMPLIANCE")
        if features.aggressive_maneuver_count > 0:
            contributing.append(f"AGGRESSIVE_MANEUVERS ({features.aggressive_maneuver_count})")
        if features.idle_ratio > 0.35:
            contributing.append("PROLONGED_IDLING_BURST")
        if features.cycle_consistency_pct < 75.0:
            contributing.append("ERRATIC_CYCLE_CONSISTENCY")

        evidence = {
            "normalized_anomaly_score": normalized_score,
            "raw_decision_score": round(raw_score, 4),
            "is_outlier_prediction": (pred == -1),
            "isolation_forest_estimators": settings.isolation_forest_n_estimators,
            "feature_attributions": contributing,
            "interpretation_note": "Score represents multivariate operational pattern deviation, not mechanical failure probability.",
        }

        return AnomalyDetectionResult(
            anomaly_detected=anomaly_detected,
            anomaly_score=normalized_score,
            decision_function_score=raw_score,
            contributing_features=contributing,
            evidence=evidence,
        )
