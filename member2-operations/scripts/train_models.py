#!/usr/bin/env python3
"""
Model Training & Artifact Serialization Pipeline.
Trains:
1. OperationalFeaturePipeline
2. ETA Regressor (Baseline, Linear, RF, Gradient Boosting comparison)
3. OperationalProxyEngine (Fuel and Idle proxies)
4. ContextSimilarityEngine (NearestNeighbors)

Serializes fitted models with joblib to member2-operations/models/
and records model_metrics.json in data/evaluation/.
"""

import json
from pathlib import Path
import sys

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
if str(OPERATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(OPERATIONS_DIR))

import joblib
import pandas as pd

from app.ml.eta_model import ETAModelWrapper, compare_candidate_models
from app.ml.features import OperationalFeaturePipeline
from app.ml.operational_proxies import OperationalProxyEngine
from app.ml.similarity import ContextSimilarityEngine

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
DATA_EVAL = OPERATIONS_DIR / "data" / "evaluation"
MODELS_DIR = OPERATIONS_DIR / "models"
METRICS_PATH = DATA_EVAL / "model_metrics.json"


def train_and_save_models():
    """Trains all operations ML and proxy models and saves artifacts."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_EVAL.mkdir(parents=True, exist_ok=True)

    train_df = pd.read_csv(DATA_EVAL / "train.csv")
    val_df = pd.read_csv(DATA_EVAL / "val.csv")

    print(f"Loaded training data ({len(train_df)} rows) and validation data ({len(val_df)} rows)")

    # 1. Fit shared feature pipeline
    feature_pipeline = OperationalFeaturePipeline()
    feature_pipeline.fit(train_df)
    X_train = feature_pipeline.transform(train_df)
    X_val = feature_pipeline.transform(val_df)
    y_train_duration = train_df["task_duration_minutes"].values
    y_val_duration = val_df["task_duration_minutes"].values

    # 2. Compare candidate ETA models
    best_eta_model, all_metrics = compare_candidate_models(
        X_train, y_train_duration, X_val, y_val_duration
    )

    # In addition, ensure we have a trained RandomForest specifically for empirical tree intervals
    rf_interval_model = ETAModelWrapper("random_forest")
    rf_interval_model.fit(X_train, y_train_duration)
    rf_metrics = rf_interval_model.evaluate(X_val, y_val_duration)

    # 3. Train Operational Proxies (Fuel & Idle)
    proxy_engine = OperationalProxyEngine()
    proxy_engine.fit(X_train, train_df)

    # 4. Train Similarity Engine on full training + reference set
    similarity_engine = ContextSimilarityEngine(n_neighbors=5)
    train_records = train_df.to_dict(orient="records")
    similarity_engine.fit(train_records)

    # 5. Save serialized artifacts
    joblib.dump(feature_pipeline, MODELS_DIR / "feature_pipeline.joblib")
    joblib.dump(best_eta_model, MODELS_DIR / "eta_model.joblib")
    joblib.dump(rf_interval_model, MODELS_DIR / "rf_interval_model.joblib")
    joblib.dump(proxy_engine, MODELS_DIR / "proxy_engine.joblib")
    joblib.dump(similarity_engine, MODELS_DIR / "similarity_engine.joblib")

    # 6. Save model_metrics.json
    metrics_report = {
        "status": "TRAINED",
        "selected_model": best_eta_model.model_type,
        "validation_metrics": all_metrics,
        "rf_interval_metrics": rf_metrics,
        "target_baseline_comparison": {
            "baseline_median_mae": all_metrics["baseline_median"]["mae"],
            "selected_model_mae": best_eta_model.metrics_["mae"],
            "mae_improvement_pct": round(
                ((all_metrics["baseline_median"]["mae"] - best_eta_model.metrics_["mae"])
                 / all_metrics["baseline_median"]["mae"]) * 100.0,
                2
            ),
        },
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_report, f, indent=2)

    print(f"All models successfully trained and saved to {MODELS_DIR}")
    print(f"Metrics written to {METRICS_PATH}")
    return metrics_report


if __name__ == "__main__":
    train_and_save_models()
