"""
Unit Tests for Feature Pipeline, ETA Model, and Operational Proxies.
Verifies ML prediction, prototype prediction intervals, fuel proxy,
productivity proxy, and similarity matching.
"""

from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd

OPERATIONS_DIR = Path(__file__).resolve().parent.parent
if str(OPERATIONS_DIR) not in sys.path:
    sys.path.insert(0, str(OPERATIONS_DIR))

from app.ml.features import OperationalFeaturePipeline
from app.ml.eta_model import ETAModelWrapper, MedianBaselineRegressor
from app.ml.operational_proxies import OperationalProxyEngine
from app.ml.similarity import ContextSimilarityEngine


class TestMLAndProxies(unittest.TestCase):
    """Test suite for machine learning and operational proxy components."""

    @classmethod
    def setUpClass(cls):
        train_path = OPERATIONS_DIR / "data" / "evaluation" / "train.csv"
        cls.train_df = pd.read_csv(train_path)
        cls.feature_pipeline = OperationalFeaturePipeline()
        cls.feature_pipeline.fit(cls.train_df)
        cls.X = cls.feature_pipeline.transform(cls.train_df)
        cls.y_duration = cls.train_df["task_duration_minutes"].values

    def test_feature_pipeline_dimensions_and_isolation(self):
        """Verify feature pipeline outputs consistent 24-dimensional float arrays."""
        self.assertEqual(self.X.shape[0], len(self.train_df))
        self.assertEqual(self.X.shape[1], 24)
        self.assertFalse(np.isnan(self.X).any())

        # Test single dict inference
        sample_dict = {
            "target_volume_tons": 500.0,
            "machine_age_years": 3.0,
            "slope_deg": 5.0,
            "ambient_temp_c": 22.0,
            "ground_saturation_pct": 15.0,
            "truck_arrival_interval_min": 5.5,
            "queue_length": 1,
            "cycle_time_sec": 28.0,
            "payload_tons": 24.0,
            "engine_load_pct": 75.0,
            "task_type": "TRENCHING",
            "weather": "CLEAR",
            "operator_skill": "EXPERT",
            "visibility_level": "GOOD",
        }
        single_x = self.feature_pipeline.transform(sample_dict)
        self.assertEqual(single_x.shape, (1, 24))

    def test_eta_model_fit_and_prediction(self):
        """Verify ETA model trains and makes plausible duration predictions."""
        model = ETAModelWrapper("random_forest")
        model.fit(self.X, self.y_duration)
        preds = model.predict(self.X[:10])
        self.assertEqual(len(preds), 10)
        self.assertTrue((preds > 10.0).all())

    def test_prototype_prediction_interval(self):
        """Verify empirical prediction interval derives lower and upper bounds."""
        model = ETAModelWrapper("random_forest")
        model.fit(self.X, self.y_duration)

        sample = self.X[0]
        res = model.predict_with_interval(sample)
        self.assertIn("predicted_minutes", res)
        self.assertIn("lower_minutes", res)
        self.assertIn("upper_minutes", res)
        self.assertIn("confidence_score", res)
        self.assertEqual(res["interval_label"], "prototype prediction interval")
        self.assertLessEqual(res["lower_minutes"], res["predicted_minutes"])
        self.assertGreaterEqual(res["upper_minutes"], res["predicted_minutes"])

    def test_baseline_heuristic_comparison(self):
        """Verify baseline median heuristic provides non-trivial baseline."""
        baseline = MedianBaselineRegressor()
        baseline.fit(self.X, self.y_duration)
        preds = baseline.predict(self.X)
        self.assertTrue((preds == np.median(self.y_duration)).all())

    def test_fuel_and_idle_proxies(self):
        """Verify transparent fuel and idle impact proxies."""
        proxy = OperationalProxyEngine()
        proxy.fit(self.X, self.train_df)

        fuel = proxy.estimate_fuel_litres(
            features=self.X[0],
            machine_model="CAT-349D",
            engine_load_pct=72.0,
            active_hours=3.0,
            idle_hours=0.5,
        )
        self.assertGreater(fuel, 10.0)

        idle = proxy.estimate_idle_minutes(
            features=self.X[0],
            queue_length=4,
            truck_arrival_interval=18.0,
            duration_minutes=240.0,
        )
        self.assertGreater(idle, 20.0)

    def test_productivity_proxy(self):
        """Verify productivity proxy computes tons/hr, pace percentage, and ratings."""
        proxy = OperationalProxyEngine()
        prod = proxy.estimate_productivity(
            target_volume_tons=850.0,
            duration_minutes=240.0,
            cycle_time_sec=28.0,
            payload_tons=24.0,
            idle_minutes=20.0,
        )
        self.assertIn("productive_output_proxy", prod)
        self.assertIn("tons_per_hour", prod)
        self.assertIn("pace_percentage", prod)
        self.assertIn("efficiency_rating", prod)
        self.assertIn(prod["efficiency_rating"], ["OPTIMAL", "HIGH", "MODERATE", "DEGRADED"])

    def test_context_similarity_engine(self):
        """Verify StandardScaler + NearestNeighbors context similarity matching."""
        sim = ContextSimilarityEngine(n_neighbors=3)
        records = self.train_df.to_dict(orient="records")
        sim.fit(records)

        query = records[0]
        matches = sim.find_similar(query, top_k=3)
        self.assertEqual(len(matches), 3)
        self.assertGreaterEqual(matches[0]["similarity_score_pct"], 90.0)

        sig = sim.compute_context_signature(query)
        self.assertTrue(sig.startswith("SIG-"))


if __name__ == "__main__":
    unittest.main()
