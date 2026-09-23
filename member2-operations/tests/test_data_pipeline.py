"""
Unit Tests for Operational Data Pipeline & Synthetic Generator.
Verifies data quality audit, deterministic reproducibility, and range validations.
"""

import json
from pathlib import Path
import unittest
import pandas as pd

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = OPERATIONS_DIR / "data" / "raw" / "raw_operational_tasks.csv"
CLEAN_CSV = OPERATIONS_DIR / "data" / "processed" / "clean_tasks.csv"
SYN_CSV = OPERATIONS_DIR / "data" / "synthetic" / "synthetic_tasks.csv"
REPORT_JSON = OPERATIONS_DIR / "data" / "evaluation" / "dataset_report.json"
TRAIN_CSV = OPERATIONS_DIR / "data" / "evaluation" / "train.csv"
TEST_CSV = OPERATIONS_DIR / "data" / "evaluation" / "test.csv"
EDGE_CSV = OPERATIONS_DIR / "data" / "evaluation" / "edge_cases.csv"


class TestDataPipeline(unittest.TestCase):
    """Test suite verifying data pipeline outputs and data governance."""

    def test_raw_dataset_exists_and_immutable(self):
        """Verify raw reference source dataset exists and has valid structure."""
        self.assertTrue(RAW_CSV.exists())
        df = pd.read_csv(RAW_CSV)
        self.assertGreaterEqual(len(df), 20)
        self.assertIn("data_origin", df.columns)
        self.assertTrue((df["data_origin"] == "SOURCE").all())

    def test_processed_dataset_clean(self):
        """Verify processed clean dataset has zero nulls and correct schema."""
        self.assertTrue(CLEAN_CSV.exists())
        df = pd.read_csv(CLEAN_CSV)
        self.assertEqual(int(df.isna().sum().sum()), 0)
        self.assertFalse(df.duplicated(subset=["task_id"]).any())

    def test_synthetic_expansion_reproducibility(self):
        """Verify synthetic dataset was generated with deterministic label."""
        self.assertTrue(SYN_CSV.exists())
        df = pd.read_csv(SYN_CSV)
        self.assertGreaterEqual(len(df), 250)
        self.assertTrue((df["data_origin"] == "SYNTHETIC").all())
        # Check realistic relationships
        self.assertTrue((df["slope_deg"] <= 15.0).all())
        self.assertTrue((df["cycle_time_sec"] >= 12.0).all())
        self.assertTrue((df["fuel_litres"] > 0).all())

    def test_dataset_report_completeness(self):
        """Verify dataset_report.json includes all required audit dimensions."""
        self.assertTrue(REPORT_JSON.exists())
        with open(REPORT_JSON, "r", encoding="utf-8") as f:
            report = json.load(f)

        required_keys = [
            "row_count",
            "columns",
            "missing_values",
            "duplicates",
            "invalid_ranges",
            "categorical_distributions",
            "numeric_ranges",
            "target_distributions",
            "split_sizes",
        ]
        for key in required_keys:
            self.assertIn(key, report)

        self.assertGreaterEqual(report["split_sizes"]["train"], 150)
        self.assertGreaterEqual(report["split_sizes"]["val"], 30)
        self.assertGreaterEqual(report["split_sizes"]["test"], 30)
        self.assertGreaterEqual(report["split_sizes"]["edge_cases"], 3)


if __name__ == "__main__":
    unittest.main()
