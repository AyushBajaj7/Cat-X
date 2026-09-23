#!/usr/bin/env python3
"""
Model Evaluation Pipeline.
Evaluates serialized models on fixed test split and operational edge cases.
Generates:
- data/evaluation/test_predictions.csv
- data/evaluation/edge_case_results.json
"""

import json
from pathlib import Path
import sys

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
if str(OPERATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(OPERATIONS_DIR))

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
DATA_EVAL = OPERATIONS_DIR / "data" / "evaluation"
MODELS_DIR = OPERATIONS_DIR / "models"
TEST_PRED_PATH = DATA_EVAL / "test_predictions.csv"
EDGE_RESULTS_PATH = DATA_EVAL / "edge_case_results.json"


def evaluate_models():
    """Runs evaluation on test set and edge cases."""
    # 1. Load artifacts
    feature_pipeline = joblib.load(MODELS_DIR / "feature_pipeline.joblib")
    eta_model = joblib.load(MODELS_DIR / "eta_model.joblib")
    rf_model = joblib.load(MODELS_DIR / "rf_interval_model.joblib")
    proxy_engine = joblib.load(MODELS_DIR / "proxy_engine.joblib")

    # 2. Evaluate on Test Split
    test_df = pd.read_csv(DATA_EVAL / "test.csv")
    X_test = feature_pipeline.transform(test_df)
    y_test_duration = test_df["task_duration_minutes"].values
    y_test_fuel = test_df["fuel_litres"].values

    test_preds_duration = eta_model.predict(X_test)

    # Calculate intervals using Random Forest
    tree_preds = np.array([tree.predict(X_test) for tree in rf_model.model.estimators_])
    lower_bounds = np.percentile(tree_preds, 10.0, axis=0)
    upper_bounds = np.percentile(tree_preds, 90.0, axis=0)

    test_results_df = test_df.copy()
    test_results_df["predicted_duration_minutes"] = np.round(test_preds_duration, 1)
    test_results_df["lower_minutes"] = np.round(lower_bounds, 1)
    test_results_df["upper_minutes"] = np.round(upper_bounds, 1)
    test_results_df["duration_error"] = np.round(test_preds_duration - y_test_duration, 1)

    test_results_df.to_csv(TEST_PRED_PATH, index=False)
    print(f"Saved test predictions to {TEST_PRED_PATH}")

    test_mae = float(mean_absolute_error(y_test_duration, test_preds_duration))
    test_rmse = float(np.sqrt(mean_squared_error(y_test_duration, test_preds_duration)))
    test_r2 = float(r2_score(y_test_duration, test_preds_duration))

    # 3. Evaluate Edge Cases
    edge_df = pd.read_csv(DATA_EVAL / "edge_cases.csv")
    X_edge = feature_pipeline.transform(edge_df)
    edge_preds = eta_model.predict(X_edge)

    edge_tree_preds = np.array([tree.predict(X_edge) for tree in rf_model.model.estimators_])
    edge_lower = np.percentile(edge_tree_preds, 10.0, axis=0)
    edge_upper = np.percentile(edge_tree_preds, 90.0, axis=0)

    edge_evaluations = []
    for i, row in edge_df.iterrows():
        pred_val = float(round(edge_preds[i], 1))
        actual_val = float(row["task_duration_minutes"])
        err = float(round(pred_val - actual_val, 1))

        # Proxy predictions
        fuel_pred = proxy_engine.estimate_fuel_litres(
            features=X_edge[i],
            machine_model=row["machine_model"],
            engine_load_pct=row["engine_load_pct"],
        )

        edge_evaluations.append({
            "task_id": row["task_id"],
            "task_type": row["task_type"],
            "scenario_name": row["site_zone"],
            "actual_duration_minutes": actual_val,
            "predicted_duration_minutes": pred_val,
            "duration_error_minutes": err,
            "prototype_prediction_interval": {
                "lower_minutes": float(round(edge_lower[i], 1)),
                "upper_minutes": float(round(edge_upper[i], 1)),
            },
            "actual_fuel_litres": float(row["fuel_litres"]),
            "predicted_fuel_litres": fuel_pred,
            "observed_idle_minutes": float(row["idle_minutes"]),
        })

    edge_report = {
        "status": "EVALUATED",
        "test_metrics": {
            "mae": round(test_mae, 2),
            "rmse": round(test_rmse, 2),
            "r2": round(test_r2, 4),
            "sample_count": len(test_df),
        },
        "edge_case_results": edge_evaluations,
    }

    with open(EDGE_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(edge_report, f, indent=2)

    print(f"Edge case evaluation written to {EDGE_RESULTS_PATH}")
    print(f"Test Set Evaluation: MAE={test_mae:.2f}, RMSE={test_rmse:.2f}, R2={test_r2:.4f}")
    return edge_report


if __name__ == "__main__":
    evaluate_models()
