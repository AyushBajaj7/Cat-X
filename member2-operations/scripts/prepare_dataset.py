#!/usr/bin/env python3
"""
Operational Data Pipeline - Dataset Preparation & Data Quality Auditing.
Reads raw challenge source data, validates ranges, missing values, duplicates,
and produces standardized clean dataset + dataset_report.json.
"""

import json
from pathlib import Path
from typing import Any, Dict
import numpy as np
import pandas as pd

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = OPERATIONS_DIR / "data" / "raw" / "raw_operational_tasks.csv"
DATA_PROCESSED = OPERATIONS_DIR / "data" / "processed" / "clean_tasks.csv"
DATA_EVALUATION = OPERATIONS_DIR / "data" / "evaluation"
REPORT_PATH = DATA_EVALUATION / "dataset_report.json"

REQUIRED_COLUMNS = [
    "task_id",
    "task_type",
    "machine_model",
    "machine_age_years",
    "operator_id",
    "operator_skill",
    "site_zone",
    "target_volume_tons",
    "weather",
    "ambient_temp_c",
    "ground_saturation_pct",
    "visibility_level",
    "slope_deg",
    "truck_arrival_interval_min",
    "queue_length",
    "cycle_time_sec",
    "payload_tons",
    "engine_load_pct",
    "idle_minutes",
    "task_duration_minutes",
    "fuel_litres",
    "shift_status",
    "data_origin",
]

NUMERIC_RANGES = {
    "machine_age_years": (0.0, 25.0),
    "target_volume_tons": (50.0, 5000.0),
    "ambient_temp_c": (-30.0, 55.0),
    "ground_saturation_pct": (0.0, 100.0),
    "slope_deg": (0.0, 35.0),
    "truck_arrival_interval_min": (0.5, 60.0),
    "queue_length": (0, 20),
    "cycle_time_sec": (10.0, 120.0),
    "payload_tons": (5.0, 60.0),
    "engine_load_pct": (10.0, 100.0),
    "idle_minutes": (0.0, 360.0),
    "task_duration_minutes": (10.0, 720.0),
    "fuel_litres": (5.0, 800.0),
}


def prepare_dataset() -> Dict[str, Any]:
    """Cleans raw dataset, performs quality checks, and outputs audit report."""
    DATA_PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    DATA_EVALUATION.mkdir(parents=True, exist_ok=True)

    if not DATA_RAW.exists():
        raise FileNotFoundError(f"Raw source dataset not found at {DATA_RAW}")

    df = pd.read_csv(DATA_RAW)

    # 1. Missing columns check
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in raw dataset: {missing_cols}")

    initial_row_count = int(len(df))

    # 2. Check duplicates
    duplicate_count = int(df.duplicated(subset=["task_id"]).sum())
    df = df.drop_duplicates(subset=["task_id"]).copy()

    # 3. Missing values check & imputation
    missing_values = {col: int(df[col].isna().sum()) for col in df.columns}

    # 4. Range validation
    invalid_ranges: Dict[str, int] = {}
    for col, (min_val, max_val) in NUMERIC_RANGES.items():
        if col in df.columns:
            invalid_mask = (df[col] < min_val) | (df[col] > max_val)
            invalid_count = int(invalid_mask.sum())
            if invalid_count > 0:
                invalid_ranges[col] = invalid_count
                df[col] = df[col].clip(min_val, max_val)

    # 5. Type normalization
    df["task_id"] = df["task_id"].astype(str)
    df["task_type"] = df["task_type"].astype(str).str.upper()
    df["machine_model"] = df["machine_model"].astype(str)
    df["operator_skill"] = df["operator_skill"].astype(str).str.upper()
    df["weather"] = df["weather"].astype(str).str.upper()
    df["visibility_level"] = df["visibility_level"].astype(str).str.upper()
    df["shift_status"] = df["shift_status"].astype(str).str.upper()
    df["data_origin"] = df["data_origin"].astype(str).str.upper()

    # Save cleaned dataset
    df.to_csv(DATA_PROCESSED, index=False)

    # 6. Gather distributions
    categorical_cols = ["task_type", "operator_skill", "weather", "visibility_level", "data_origin"]
    categorical_distributions = {
        col: {str(k): int(v) for k, v in df[col].value_counts().to_dict().items()}
        for col in categorical_cols
    }

    numeric_summary = {}
    for col in NUMERIC_RANGES.keys():
        if col in df.columns:
            numeric_summary[col] = {
                "min": float(round(df[col].min(), 2)),
                "max": float(round(df[col].max(), 2)),
                "mean": float(round(df[col].mean(), 2)),
                "median": float(round(df[col].median(), 2)),
                "std": float(round(df[col].std(), 2)) if len(df) > 1 else 0.0,
            }

    target_distributions = {
        "task_duration_minutes": {
            "mean": float(round(df["task_duration_minutes"].mean(), 2)),
            "std": float(round(df["task_duration_minutes"].std(), 2)) if len(df) > 1 else 0.0,
            "p10": float(round(df["task_duration_minutes"].quantile(0.10), 2)),
            "p50": float(round(df["task_duration_minutes"].quantile(0.50), 2)),
            "p90": float(round(df["task_duration_minutes"].quantile(0.90), 2)),
        },
        "fuel_litres": {
            "mean": float(round(df["fuel_litres"].mean(), 2)),
            "p50": float(round(df["fuel_litres"].quantile(0.50), 2)),
        },
    }

    report = {
        "pipeline_status": "READY",
        "row_count": int(len(df)),
        "initial_raw_count": initial_row_count,
        "columns": list(df.columns),
        "missing_values": missing_values,
        "duplicates": duplicate_count,
        "invalid_ranges": invalid_ranges,
        "categorical_distributions": categorical_distributions,
        "numeric_ranges": numeric_summary,
        "target_distributions": target_distributions,
        "split_sizes": {
            "train": 0,
            "val": 0,
            "test": 0,
            "edge_cases": 0,
        },
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Data preparation complete: {len(df)} records processed to {DATA_PROCESSED}")
    print(f"Dataset report written to {REPORT_PATH}")
    return report


if __name__ == "__main__":
    prepare_dataset()
