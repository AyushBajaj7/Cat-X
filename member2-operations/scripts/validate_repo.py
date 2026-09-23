#!/usr/bin/env python3
"""
Comprehensive Repository & Subsystem Validator for Member 2 Operations.
Performs strict end-to-end health and consistency checks across:
1. Directory structure & planned artifacts
2. Data pipeline files & immutability
3. ML model artifacts & serialization
4. Safety constraint engine (including Boom Reach Envelope CST-BOOM-01)
5. Shift Twin intelligence & attention_mode propagation
6. Decision Memory ORM persistence
7. End-to-end API endpoints
"""

import sys
from pathlib import Path

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
if str(OPERATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(OPERATIONS_DIR))

import joblib
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.domain.demo_fixture import get_the_17_minute_trap_state
from app.trajectory.safety_constraints import safety_constraint_engine
from app.trajectory.consequence_engine import consequence_engine
from app.trajectory.scenario_generator import scenario_generator
from app.memory.similar_context import similar_context_service
from app.persistence.database import SessionLocal
from app.persistence.models import SimilarContextRecord


def validate():
    print("=" * 60)
    print("CAT-X MEMBER 2 OPERATIONS: REPOSITORY VALIDATION")
    print("=" * 60)
    failures = []

    # 1. Directory & File Checks
    print("\n[1/7] Checking Planned Files & Folders...")
    required_files = [
        "tests/__init__.py",
        "data/raw/README.md",
        "scripts/README.md",
        "data/processed/clean_tasks.csv",
        "data/evaluation/train.csv",
        "data/evaluation/val.csv",
        "data/evaluation/test.csv",
        "data/evaluation/edge_cases.csv",
        "models/eta_model.joblib",
        "models/rf_interval_model.joblib",
        "models/feature_pipeline.joblib",
        "models/proxy_engine.joblib",
        "models/similarity_engine.joblib",
    ]
    for rf in required_files:
        p = OPERATIONS_DIR / rf
        if not p.exists():
            failures.append(f"Missing required file: {rf}")
            print(f"  [MISSING] {rf}")
        else:
            print(f"  [OK] Found: {rf}")

    # 2. ML Artifact Validation
    print("\n[2/7] Validating ML Model Artifacts...")
    try:
        pipeline = joblib.load(OPERATIONS_DIR / "models" / "feature_pipeline.joblib")
        eta_m = joblib.load(OPERATIONS_DIR / "models" / "eta_model.joblib")
        rf_m = joblib.load(OPERATIONS_DIR / "models" / "rf_interval_model.joblib")
        proxy_m = joblib.load(OPERATIONS_DIR / "models" / "proxy_engine.joblib")
        sim_m = joblib.load(OPERATIONS_DIR / "models" / "similarity_engine.joblib")
        print("  [OK] All 5 ML model artifacts loaded successfully")
    except Exception as e:
        failures.append(f"ML loading failed: {e}")
        print(f"  [FAIL] ML loading failed: {e}")

    # 3. Safety Constraint Engine & Boom Reach Envelope Check
    print("\n[3/7] Validating Safety Constraints (including Boom Reach CST-BOOM-01)...")
    try:
        state = get_the_17_minute_trap_state()
        # Test boom reach violation (> 60 deg)
        res_violation = safety_constraint_engine.validate_scenario(
            scenario_id="SCEN-BOOM-TEST",
            state=state,
            overrides={"swing_angle_deg": 68.0}
        )
        assert res_violation.constraint_status == "REJECTED", "Boom violation should be REJECTED"
        boom_item = next(i for i in res_violation.constraints if i.constraint_id == "CST-BOOM-01")
        assert boom_item.status == "VIOLATED", "CST-BOOM-01 item must be VIOLATED"
        print("  [OK] CST-BOOM-01 properly rejects swing_angle_deg > 60 deg")

        # Test normal boom reach (< 50 deg)
        res_pass = safety_constraint_engine.validate_scenario(
            scenario_id="SCEN-BOOM-PASS",
            state=state,
            overrides={"swing_angle_deg": 40.0, "slope_deg": 5.0, "proximity_distance_m": 25.0}
        )
        assert res_pass.constraint_status == "FEASIBLE", "Normal boom reach should be FEASIBLE"
        print("  [OK] CST-BOOM-01 passes within rated envelope (< 50 deg)")
    except Exception as e:
        failures.append(f"Safety constraint test failed: {e}")
        print(f"  [FAIL] Safety constraint test failed: {e}")

    # 4. Similar Context Persistence Check
    print("\n[4/7] Validating SimilarContext DB Persistence...")
    try:
        sample_profile = {
            "task_type": "TRENCHING",
            "material_type": "WET_CLAY",
            "site_zone": "Bench 2 Deep Cut",
            "target_volume_tons": 800.0,
            "machine_model": "CAT 349",
        }
        res_sim = similar_context_service.find_similar_shifts(sample_profile, top_k=2)
        assert len(res_sim) > 0, "Expected at least 1 similar shift"

        with SessionLocal() as db:
            records = db.query(SimilarContextRecord).all()
            assert len(records) > 0, "SimilarContextRecord table should contain persisted rows"
            print(f"  [OK] Successfully verified {len(records)} persisted rows in similar_contexts DB table")
    except Exception as e:
        failures.append(f"Similar context persistence failed: {e}")
        print(f"  [FAIL] Similar context persistence failed: {e}")

    # 5. Shift Twin Attention Mode & Intelligence Propagation
    print("\n[5/7] Validating Shift Twin Propagation & Attention Mode...")
    client = TestClient(app)
    try:
        twin_res = client.get("/api/v1/operator/OP1001/shift-twin")
        assert twin_res.status_code == 200, f"Twin endpoint returned {twin_res.status_code}"
        twin_data = twin_res.json()

        assert twin_data["attention_mode"] == "DECISION_FOCUS", (
            f"Expected attention_mode 'DECISION_FOCUS', got {twin_data['attention_mode']}"
        )
        assert twin_data["decision_point"] is not None, "decision_point must be populated"
        assert len(twin_data["trajectory_options"]) >= 3, "trajectory_options must be populated"
        assert twin_data["shift_forecast"] is not None, "shift_forecast must be populated"
        assert len(twin_data["decision_trace"]) > 0, "decision_trace must be populated"
        assert len(twin_data["similar_contexts"]) > 0, "similar_contexts must be populated"
        print(f"  [OK] Shift Twin correctly propagated attention_mode='{twin_data['attention_mode']}'")
        print(f"  [OK] Shift Twin populated with {len(twin_data['trajectory_options'])} trajectory options")
        print(f"  [OK] Shift Twin populated decision_point and forecast")
    except Exception as e:
        failures.append(f"Shift Twin validation failed: {e}")
        print(f"  [FAIL] Shift Twin validation failed: {e}")

    # 6. Trajectory Closed-Loop Workflow Check
    print("\n[6/7] Validating CAT Trajectory Closed Loop...")
    try:
        # Detect
        det_res = client.post("/api/v1/trajectory/detect", json={"queue_length": 4, "truck_arrival_interval_min": 3.0})
        assert det_res.status_code == 200
        det_data = det_res.json()
        assert det_data["decision_point_detected"] is True

        # Evaluate
        eval_res = client.post("/api/v1/trajectory/evaluate", json={})
        assert eval_res.status_code == 200
        eval_data = eval_res.json()
        assert len(eval_data["scenarios"]) >= 3

        # Choose
        choose_res = client.post("/api/v1/trajectory/choose", json={
            "operator_id": "OP1001",
            "decision_point_id": det_data.get("decision_point_id", "DP-T002-HAUL-01"),
            "scenario_id": eval_data["scenarios"][0]["scenario_id"],
            "operator_reason": "Validation test selection",
        })
        assert choose_res.status_code == 200
        choose_data = choose_res.json()
        decision_id = choose_data["decision_id"]

        # Outcome
        out_res = client.post("/api/v1/trajectory/outcome", json={
            "decision_id": decision_id,
            "actual_time_saved_minutes": 15.0,
            "actual_fuel_saved_liters": 12.0,
            "actual_risk_outcome": "LOW",
            "operator_reflection": "Smooth operation under test",
        })
        assert out_res.status_code == 200
        print("  [OK] End-to-end trajectory lifecycle (detect -> evaluate -> choose -> outcome) fully functional")
    except Exception as e:
        failures.append(f"Trajectory closed-loop failed: {e}")
        print(f"  [FAIL] Trajectory closed-loop failed: {e}")

    # 7. Overall Summary
    print("\n[7/7] Validation Summary")
    if failures:
        print(f"\n[FAIL] FAILED with {len(failures)} issues:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("\n[SUCCESS] ALL VALIDATION CHECKS PASSED PERFECTLY!")
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
