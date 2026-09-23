#!/usr/bin/env python3
"""
Deterministic Synthetic Telemetry & Operational Task Expansion Generator.
Generates physics-consistent heavy machine operational data calibrated against
published Caterpillar 349 Excavator, 740 GC Truck, and D8T Dozer operational parameters.

Explicitly labels all generated records with data_origin="SYNTHETIC".
Never presents generated data as proprietary Caterpillar telemetry.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import pandas as pd

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
DATA_PROCESSED = OPERATIONS_DIR / "data" / "processed" / "clean_tasks.csv"
DATA_SYNTHETIC = OPERATIONS_DIR / "data" / "synthetic" / "synthetic_tasks.csv"
DATA_EVAL = OPERATIONS_DIR / "data" / "evaluation"
REPORT_PATH = DATA_EVAL / "dataset_report.json"

TASK_PROFILES = {
    "EXCAVATION": {"base_rate": 3.8, "base_cycle": 28.0, "base_load": 72.0, "machine": "CAT-349D"},
    "TRENCHING": {"base_rate": 3.2, "base_cycle": 32.0, "base_load": 70.0, "machine": "CAT-349D"},
    "LOADING": {"base_rate": 4.5, "base_cycle": 22.0, "base_load": 82.0, "machine": "CAT-349D"},
    "GRADING": {"base_rate": 2.8, "base_cycle": 30.0, "base_load": 68.0, "machine": "CAT-D8T"},
    "OVERBURDEN": {"base_rate": 4.0, "base_cycle": 24.0, "base_load": 76.0, "machine": "CAT-349D"},
}

SKILL_MULTIPLIERS = {
    "NOVICE": {"cycle_mult": 1.18, "idle_mult": 1.25, "fuel_mult": 1.08},
    "INTERMEDIATE": {"cycle_mult": 1.00, "idle_mult": 1.00, "fuel_mult": 1.00},
    "EXPERT": {"cycle_mult": 0.88, "idle_mult": 0.78, "fuel_mult": 0.94},
    "MASTER": {"cycle_mult": 0.82, "idle_mult": 0.70, "fuel_mult": 0.90},
}

WEATHER_EFFECTS = {
    "CLEAR": {"speed_factor": 1.00, "saturation_range": (5.0, 15.0), "temp_range": (20.0, 32.0), "vis": "EXCELLENT"},
    "OVERCAST": {"speed_factor": 0.96, "saturation_range": (10.0, 20.0), "temp_range": (16.0, 24.0), "vis": "GOOD"},
    "RAIN": {"speed_factor": 0.84, "saturation_range": (24.0, 38.0), "temp_range": (14.0, 20.0), "vis": "MODERATE"},
    "MUD": {"speed_factor": 0.72, "saturation_range": (35.0, 55.0), "temp_range": (12.0, 18.0), "vis": "POOR"},
    "FOG": {"speed_factor": 0.88, "saturation_range": (15.0, 25.0), "temp_range": (10.0, 16.0), "vis": "POOR"},
}

ZONES = ["ZONE_4_NORTH", "BENCH_2_WEST", "STOCKPILE_1", "STOCKPILE_2", "HAUL_ROAD_EAST", "BENCH_3_UPPER", "RAMP_3_SOUTH"]


def generate_synthetic_dataset(n_samples: int = 280, seed: int = 42) -> pd.DataFrame:
    """Generates synthetic tasks with physics-correlated features."""
    rng = np.random.default_rng(seed)

    records: List[Dict[str, Any]] = []

    task_types = list(TASK_PROFILES.keys())
    operator_skills = list(SKILL_MULTIPLIERS.keys())
    weathers = list(WEATHER_EFFECTS.keys())

    for i in range(1, n_samples + 1):
        task_id = f"T-SYN-{i:04d}"
        task_type = rng.choice(task_types, p=[0.25, 0.25, 0.20, 0.15, 0.15])
        profile = TASK_PROFILES[task_type]
        machine_model = profile["machine"]
        machine_age = float(round(rng.uniform(0.5, 8.0), 1))
        operator_skill = rng.choice(operator_skills, p=[0.20, 0.40, 0.30, 0.10])
        skill_mods = SKILL_MULTIPLIERS[operator_skill]
        operator_id = f"OP{rng.integers(1001, 1025)}"
        site_zone = rng.choice(ZONES)

        weather = rng.choice(weathers, p=[0.40, 0.25, 0.20, 0.10, 0.05])
        w_effect = WEATHER_EFFECTS[weather]
        ambient_temp = float(round(rng.uniform(*w_effect["temp_range"]), 1))
        ground_saturation = float(round(rng.uniform(*w_effect["saturation_range"]), 1))
        visibility = w_effect["vis"]

        slope = float(round(rng.exponential(scale=3.5), 1))
        slope = min(slope, 14.5)  # Stay below hard catastrophic limit for nominal records

        # Target volume
        if task_type in ["LOADING", "OVERBURDEN"]:
            target_volume = float(round(rng.uniform(600, 1600), 0))
        elif task_type == "TRENCHING":
            target_volume = float(round(rng.uniform(400, 1000), 0))
        else:
            target_volume = float(round(rng.uniform(300, 800), 0))

        # Fleet logistics (truck arrival interval & queue)
        is_bunched = rng.random() < 0.22  # 22% chance of fleet cycle bottleneck
        if is_bunched:
            truck_arrival_interval = float(round(rng.uniform(11.0, 22.0), 1))
            queue_length = int(rng.integers(3, 7))
        else:
            truck_arrival_interval = float(round(rng.uniform(3.5, 7.5), 1))
            queue_length = int(rng.integers(0, 3))

        # Cycle time with physics adjustments
        cycle_time = profile["base_cycle"] * skill_mods["cycle_mult"]
        cycle_time += (ground_saturation - 10.0) * 0.25
        cycle_time += slope * 0.45
        cycle_time = float(round(max(15.0, cycle_time + rng.normal(0, 1.5)), 1))

        # Payload
        nominal_payload = 26.0 if machine_model == "CAT-349D" else 18.0
        payload = float(round(max(12.0, nominal_payload + rng.normal(0, 1.8)), 1))

        # Engine load
        engine_load = profile["base_load"] + (slope * 0.8) + ((ground_saturation - 10.0) * 0.3)
        engine_load = float(round(np.clip(engine_load + rng.normal(0, 2.5), 45.0, 95.0), 1))

        # Idle minutes: compounding queue / bottleneck effects
        active_cycles = target_volume / max(1.0, (payload / (cycle_time / 30.0)))
        active_time_minutes = (active_cycles * cycle_time) / 60.0

        base_idle = (active_time_minutes * 0.08) * skill_mods["idle_mult"]
        if is_bunched:
            queue_idle = (truck_arrival_interval * 0.8) * queue_length * 0.4
            idle_minutes = float(round(base_idle + queue_idle + rng.uniform(4.0, 12.0), 1))
        else:
            idle_minutes = float(round(base_idle + rng.uniform(1.0, 6.0), 1))

        # Total duration
        weather_delay = 0.0
        if weather in ["RAIN", "MUD"]:
            weather_delay = active_time_minutes * (1.0 - w_effect["speed_factor"])
        total_duration = float(round(active_time_minutes + idle_minutes + weather_delay, 1))

        # Fuel consumption proxy:
        # Active fuel: ~36 L/hr for 349D at load, ~26 L/hr for D8T
        # High/low idle: ~14 L/hr
        active_rate_lph = (36.0 if machine_model == "CAT-349D" else 26.0) * (engine_load / 75.0) * skill_mods["fuel_mult"]
        idle_rate_lph = 13.5
        fuel_litres = float(round(
            ((active_time_minutes / 60.0) * active_rate_lph) +
            ((idle_minutes / 60.0) * idle_rate_lph),
            1
        ))

        shift_status = rng.choice(["COMPLETED", "IN_PROGRESS", "COMPLETED", "COMPLETED"])

        records.append({
            "task_id": task_id,
            "task_type": task_type,
            "machine_model": machine_model,
            "machine_age_years": machine_age,
            "operator_id": operator_id,
            "operator_skill": operator_skill,
            "site_zone": site_zone,
            "target_volume_tons": target_volume,
            "weather": weather,
            "ambient_temp_c": ambient_temp,
            "ground_saturation_pct": ground_saturation,
            "visibility_level": visibility,
            "slope_deg": slope,
            "truck_arrival_interval_min": truck_arrival_interval,
            "queue_length": queue_length,
            "cycle_time_sec": cycle_time,
            "payload_tons": payload,
            "engine_load_pct": engine_load,
            "idle_minutes": idle_minutes,
            "task_duration_minutes": total_duration,
            "fuel_litres": fuel_litres,
            "shift_status": shift_status,
            "data_origin": "SYNTHETIC",
        })

    return pd.DataFrame(records)


def generate_edge_cases() -> pd.DataFrame:
    """Explicitly builds operational edge cases including 'The 17-Minute Trap'."""
    edge_records = [
        # 1. The 17-Minute Trap (Bench 2 Haul Bottleneck + Rain)
        {
            "task_id": "EDGE-17MIN-TRAP",
            "task_type": "TRENCHING",
            "machine_model": "CAT-349D",
            "machine_age_years": 3.5,
            "operator_id": "OP1001",
            "operator_skill": "INTERMEDIATE",
            "site_zone": "BENCH_2_WEST",
            "target_volume_tons": 850.0,
            "weather": "RAIN",
            "ambient_temp_c": 18.0,
            "ground_saturation_pct": 28.0,
            "visibility_level": "MODERATE",
            "slope_deg": 7.5,
            "truck_arrival_interval_min": 18.2,
            "queue_length": 4,
            "cycle_time_sec": 34.0,
            "payload_tons": 22.0,
            "engine_load_pct": 68.0,
            "idle_minutes": 42.0,
            "task_duration_minutes": 257.0,  # +17 minutes past 240 scheduled
            "fuel_litres": 215.0,
            "shift_status": "IN_PROGRESS",
            "data_origin": "SYNTHETIC",
        },
        # 2. Extreme Idle Trap (Crusher breakdown)
        {
            "task_id": "EDGE-EXTREME-IDLE",
            "task_type": "LOADING",
            "machine_model": "CAT-349D",
            "machine_age_years": 4.0,
            "operator_id": "OP1002",
            "operator_skill": "EXPERT",
            "site_zone": "STOCKPILE_1",
            "target_volume_tons": 1000.0,
            "weather": "CLEAR",
            "ambient_temp_c": 28.0,
            "ground_saturation_pct": 8.0,
            "visibility_level": "EXCELLENT",
            "slope_deg": 1.0,
            "truck_arrival_interval_min": 35.0,
            "queue_length": 6,
            "cycle_time_sec": 22.0,
            "payload_tons": 27.0,
            "engine_load_pct": 52.0,
            "idle_minutes": 68.0,
            "task_duration_minutes": 270.0,
            "fuel_litres": 185.0,
            "shift_status": "IN_PROGRESS",
            "data_origin": "SYNTHETIC",
        },
        # 3. Severe Mud Ground Saturation Slip
        {
            "task_id": "EDGE-MUD-SLIP",
            "task_type": "EXCAVATION",
            "machine_model": "CAT-349D",
            "machine_age_years": 5.0,
            "operator_id": "OP1005",
            "operator_skill": "NOVICE",
            "site_zone": "ZONE_4_NORTH",
            "target_volume_tons": 600.0,
            "weather": "MUD",
            "ambient_temp_c": 12.0,
            "ground_saturation_pct": 48.0,
            "visibility_level": "POOR",
            "slope_deg": 11.5,
            "truck_arrival_interval_min": 15.0,
            "queue_length": 3,
            "cycle_time_sec": 44.0,
            "payload_tons": 18.5,
            "engine_load_pct": 88.0,
            "idle_minutes": 38.0,
            "task_duration_minutes": 285.0,
            "fuel_litres": 224.0,
            "shift_status": "COMPLETED",
            "data_origin": "SYNTHETIC",
        },
        # 4. Critical Slope Limit Proximity
        {
            "task_id": "EDGE-SLOPE-LIMIT",
            "task_type": "GRADING",
            "machine_model": "CAT-D8T",
            "machine_age_years": 6.5,
            "operator_id": "OP1003",
            "operator_skill": "NOVICE",
            "site_zone": "RAMP_3_SOUTH",
            "target_volume_tons": 400.0,
            "weather": "RAIN",
            "ambient_temp_c": 16.0,
            "ground_saturation_pct": 32.0,
            "visibility_level": "MODERATE",
            "slope_deg": 14.8,  # Close to 15.0 limit
            "truck_arrival_interval_min": 10.0,
            "queue_length": 1,
            "cycle_time_sec": 38.0,
            "payload_tons": 17.0,
            "engine_load_pct": 89.0,
            "idle_minutes": 25.0,
            "task_duration_minutes": 220.0,
            "fuel_litres": 170.0,
            "shift_status": "COMPLETED",
            "data_origin": "SYNTHETIC",
        },
        # 5. Fast Master Loading Benchmark
        {
            "task_id": "EDGE-MASTER-BENCHMARK",
            "task_type": "LOADING",
            "machine_model": "CAT-349D",
            "machine_age_years": 1.5,
            "operator_id": "OP1004",
            "operator_skill": "MASTER",
            "site_zone": "STOCKPILE_2",
            "target_volume_tons": 1500.0,
            "weather": "CLEAR",
            "ambient_temp_c": 24.0,
            "ground_saturation_pct": 7.0,
            "visibility_level": "EXCELLENT",
            "slope_deg": 1.0,
            "truck_arrival_interval_min": 3.2,
            "queue_length": 1,
            "cycle_time_sec": 19.5,
            "payload_tons": 29.0,
            "engine_load_pct": 84.0,
            "idle_minutes": 8.0,
            "task_duration_minutes": 225.0,
            "fuel_litres": 210.0,
            "shift_status": "COMPLETED",
            "data_origin": "SYNTHETIC",
        },
    ]
    return pd.DataFrame(edge_records)


def main():
    """Generates synthetic tasks, saves splits, and updates dataset_report.json."""
    DATA_SYNTHETIC.parent.mkdir(parents=True, exist_ok=True)
    DATA_EVAL.mkdir(parents=True, exist_ok=True)

    # 1. Load cleaned source dataset
    source_df = pd.read_csv(DATA_PROCESSED)
    print(f"Loaded {len(source_df)} reference records from {DATA_PROCESSED}")

    # 2. Generate 280 synthetic tasks deterministically
    synthetic_df = generate_synthetic_dataset(n_samples=280, seed=42)
    synthetic_df.to_csv(DATA_SYNTHETIC, index=False)
    print(f"Generated {len(synthetic_df)} synthetic records to {DATA_SYNTHETIC}")

    # 3. Combine source + synthetic
    combined_df = pd.concat([source_df, synthetic_df], ignore_index=True)

    # Shuffle deterministically
    rng = np.random.default_rng(seed=42)
    shuffled_indices = rng.permutation(len(combined_df))
    shuffled_df = combined_df.iloc[shuffled_indices].reset_index(drop=True)

    # 4. Create Train (70%), Val (15%), Test (15%) splits
    n_total = len(shuffled_df)
    n_train = int(n_total * 0.70)
    n_val = int(n_total * 0.15)

    train_df = shuffled_df.iloc[:n_train].copy()
    val_df = shuffled_df.iloc[n_train:n_train + n_val].copy()
    test_df = shuffled_df.iloc[n_train + n_val:].copy()

    # 5. Generate edge cases
    edge_df = generate_edge_cases()

    # Save evaluation splits
    train_path = DATA_EVAL / "train.csv"
    val_path = DATA_EVAL / "val.csv"
    test_path = DATA_EVAL / "test.csv"
    edge_path = DATA_EVAL / "edge_cases.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    edge_df.to_csv(edge_path, index=False)

    print(f"Splits created: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}, Edge={len(edge_df)}")

    # 6. Update dataset_report.json
    if REPORT_PATH.exists():
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report = json.load(f)
    else:
        report = {}

    report["row_count"] = n_total
    report["split_sizes"] = {
        "train": len(train_df),
        "val": len(val_df),
        "test": len(test_df),
        "edge_cases": len(edge_df),
        "source_records": int((combined_df["data_origin"] == "SOURCE").sum()),
        "synthetic_records": int((combined_df["data_origin"] == "SYNTHETIC").sum()),
    }
    report["target_distributions"] = {
        "task_duration_minutes": {
            "mean": float(round(combined_df["task_duration_minutes"].mean(), 2)),
            "std": float(round(combined_df["task_duration_minutes"].std(), 2)),
            "p10": float(round(combined_df["task_duration_minutes"].quantile(0.10), 2)),
            "p50": float(round(combined_df["task_duration_minutes"].quantile(0.50), 2)),
            "p90": float(round(combined_df["task_duration_minutes"].quantile(0.90), 2)),
        },
        "fuel_litres": {
            "mean": float(round(combined_df["fuel_litres"].mean(), 2)),
            "p50": float(round(combined_df["fuel_litres"].quantile(0.50), 2)),
        },
        "idle_minutes": {
            "mean": float(round(combined_df["idle_minutes"].mean(), 2)),
            "p50": float(round(combined_df["idle_minutes"].quantile(0.50), 2)),
        },
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Updated {REPORT_PATH} with split metrics and target distributions.")


if __name__ == "__main__":
    main()
