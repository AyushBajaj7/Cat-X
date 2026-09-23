"""
Probabilistic Task ETA Estimator & Prediction Interval Engine.
Evaluates baseline median against Linear Regression, Random Forest, and Gradient Boosting.
Provides empirical prototype prediction intervals (P10/P90) derived from tree estimators.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class MedianBaselineRegressor:
    """Baseline heuristic predicting historical median duration."""

    def __init__(self):
        self.median_val: float = 180.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.median_val = float(np.median(y))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(shape=(X.shape[0],), fill_value=self.median_val, dtype=np.float64)


class ETAModelWrapper:
    """Production wrapper for task duration prediction with empirical prediction intervals."""

    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        if model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, min_samples_split=4)
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42, learning_rate=0.08)
        elif model_type == "linear":
            self.model = LinearRegression()
        elif model_type == "baseline_median":
            self.model = MedianBaselineRegressor()
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        self.is_fitted: bool = False
        self.metrics_: Dict[str, float] = {}

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fits the underlying regression estimator."""
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Returns point predictions."""
        if not self.is_fitted:
            raise RuntimeError("ETAModelWrapper must be fitted before predict.")
        return self.model.predict(X)

    def predict_with_interval(
        self,
        X: np.ndarray,
        p_lower: float = 10.0,
        p_upper: float = 90.0
    ) -> Dict[str, Any]:
        """
        Returns point estimate, prototype prediction interval (lower_minutes, upper_minutes),
        and confidence score.
        """
        if not self.is_fitted:
            raise RuntimeError("ETAModelWrapper must be fitted before predict_with_interval.")

        # Ensure 2D input
        if len(X.shape) == 1:
            X_in = X.reshape(1, -1)
        else:
            X_in = X

        point_pred = self.model.predict(X_in)

        if isinstance(self.model, RandomForestRegressor) and hasattr(self.model, "estimators_"):
            # Derive empirical distribution across all tree estimators
            tree_preds = np.array([tree.predict(X_in) for tree in self.model.estimators_])  # shape: (n_trees, n_samples)
            lower_bounds = np.percentile(tree_preds, p_lower, axis=0)
            upper_bounds = np.percentile(tree_preds, p_upper, axis=0)
            std_devs = np.std(tree_preds, axis=0)

            # Confidence score inversely proportional to variance relative to mean
            rel_uncertainty = std_devs / np.maximum(point_pred, 1.0)
            confidence_scores = np.clip(1.0 - (rel_uncertainty * 1.8), 0.50, 0.98)
        else:
            # Fallback heuristic for non-tree models (e.g. baseline or linear)
            lower_bounds = point_pred * 0.88
            upper_bounds = point_pred * 1.15
            confidence_scores = np.full_like(point_pred, fill_value=0.75)

        return {
            "predicted_minutes": float(np.round(point_pred[0], 1)),
            "lower_minutes": float(np.round(lower_bounds[0], 1)),
            "upper_minutes": float(np.round(upper_bounds[0], 1)),
            "confidence_score": float(np.round(confidence_scores[0], 2)),
            "interval_label": "prototype prediction interval",
        }

    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, float]:
        """Evaluates model on validation data returning MAE, RMSE, and R2."""
        preds = self.predict(X_val)
        mae = float(mean_absolute_error(y_val, preds))
        rmse = float(np.sqrt(mean_squared_error(y_val, preds)))
        r2 = float(r2_score(y_val, preds))
        self.metrics_ = {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
        }
        return self.metrics_


def compare_candidate_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray
) -> Tuple[ETAModelWrapper, Dict[str, Dict[str, float]]]:
    """Compares candidate models on validation split and selects the best by MAE."""
    candidates = {
        "baseline_median": ETAModelWrapper("baseline_median"),
        "linear_regression": ETAModelWrapper("linear"),
        "random_forest": ETAModelWrapper("random_forest"),
        "gradient_boosting": ETAModelWrapper("gradient_boosting"),
    }

    all_metrics = {}
    best_name = "random_forest"
    best_mae = float("inf")
    best_wrapper = None

    for name, wrapper in candidates.items():
        wrapper.fit(X_train, y_train)
        metrics = wrapper.evaluate(X_val, y_val)
        all_metrics[name] = metrics
        if metrics["mae"] < best_mae:
            best_mae = metrics["mae"]
            best_name = name
            best_wrapper = wrapper

    print(f"Candidate model comparison complete. Best: {best_name} (MAE={best_mae:.2f})")
    return best_wrapper, all_metrics
