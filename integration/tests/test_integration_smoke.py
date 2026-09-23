"""Cross-service integration and schema contract smoke tests."""

import json
from pathlib import Path
import pytest


CONTRACTS_DIR = Path(__file__).resolve().parent.parent.parent / "shared" / "contracts"


def test_contracts_exist_and_are_valid_json():
    """Verify all 7 mandatory JSON schema contracts exist and are valid JSON."""
    expected_schemas = [
        "telemetry.schema.json",
        "safety.schema.json",
        "behaviour.schema.json",
        "task.schema.json",
        "prediction.schema.json",
        "shift-twin.schema.json",
        "decision-point.schema.json",
        "scenario.schema.json",
        "consequence.schema.json",
        "decision-memory.schema.json",
        "training.schema.json",
        "dashboard.schema.json",
        "error.schema.json",
    ]

    for schema_file in expected_schemas:
        schema_path = CONTRACTS_DIR / schema_file
        assert schema_path.exists(), f"Missing schema contract: {schema_file}"
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "$schema" in data or "type" in data
            assert "title" in data


def test_shift_twin_canonical_structure():
    """Verify Shift Twin schema requires the 7 contextual dimensions."""
    twin_schema_path = CONTRACTS_DIR / "shift-twin.schema.json"
    with open(twin_schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    twin_def = schema["definitions"]["ShiftTwin"]
    required_fields = twin_def["required"]

    mandatory_dimensions = [
        "operator_id",
        "machine_id",
        "environment",
        "safety",
        "behaviour",
        "productivity",
        "prediction",
        "next_best_actions",
    ]

    for dim in mandatory_dimensions:
        assert dim in required_fields, f"Shift Twin missing mandatory dimension: {dim}"
