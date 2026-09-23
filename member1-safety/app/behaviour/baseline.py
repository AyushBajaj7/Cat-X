"""Operator statistical profile baseline management."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from ..models import BehaviourSignal, SignalType, TrendDirection
from .features import BehaviourFeatures


@dataclass
class OperatorBaseline:
    """Historical mean and standard deviation profile for an operator."""

    operator_id: str
    sample_count: int = 0
    means: Dict[str, float] = field(default_factory=dict)
    stds: Dict[str, float] = field(default_factory=dict)


class BaselineManager:
    """Computes and tracks statistical baseline behavior for machine operators."""

    def __init__(self):
        # operator_id -> OperatorBaseline
        self._baselines: Dict[str, OperatorBaseline] = {}

    def get_or_create_baseline(self, operator_id: str) -> OperatorBaseline:
        if operator_id not in self._baselines:
            # Seed with site-wide nominal baseline defaults
            self._baselines[operator_id] = OperatorBaseline(
                operator_id=operator_id,
                sample_count=20,
                means={
                    "mean_speed_mps": 1.6,
                    "max_speed_mps": 3.4,
                    "mean_rpm": 1780.0,
                    "mean_fuel_rate_lph": 16.5,
                    "idle_ratio": 0.12,
                    "mean_fatigue": 25.0,
                    "seatbelt_compliance_pct": 98.0,
                    "aggressive_maneuver_count": 0.1,
                    "unsafe_speed_events": 0.05,
                    "cycle_consistency_pct": 92.0,
                },
                stds={
                    "mean_speed_mps": 0.4,
                    "max_speed_mps": 0.8,
                    "mean_rpm": 120.0,
                    "mean_fuel_rate_lph": 2.2,
                    "idle_ratio": 0.05,
                    "mean_fatigue": 8.0,
                    "seatbelt_compliance_pct": 3.0,
                    "aggressive_maneuver_count": 0.5,
                    "unsafe_speed_events": 0.3,
                    "cycle_consistency_pct": 4.0,
                },
            )
        return self._baselines[operator_id]

    def update_baseline(self, operator_id: str, features: BehaviourFeatures) -> OperatorBaseline:
        """Update operator running baseline with new observed window."""
        bl = self.get_or_create_baseline(operator_id)
        bl.sample_count += 1
        alpha = 0.1  # Exponential moving average weight

        feat_dict = {
            "mean_speed_mps": features.mean_speed_mps,
            "max_speed_mps": features.max_speed_mps,
            "mean_rpm": features.mean_rpm,
            "mean_fuel_rate_lph": features.mean_fuel_rate_lph,
            "idle_ratio": features.idle_ratio,
            "mean_fatigue": features.mean_fatigue,
            "seatbelt_compliance_pct": features.seatbelt_compliance_pct,
            "aggressive_maneuver_count": float(features.aggressive_maneuver_count),
            "unsafe_speed_events": float(features.unsafe_speed_events),
            "cycle_consistency_pct": features.cycle_consistency_pct,
        }

        for k, v in feat_dict.items():
            old_mean = bl.means.get(k, v)
            old_std = bl.stds.get(k, 1.0)
            new_mean = (1 - alpha) * old_mean + alpha * v
            # Update running variance estimate
            diff = abs(v - new_mean)
            new_std = max(0.01, (1 - alpha) * old_std + alpha * diff)

            bl.means[k] = round(new_mean, 2)
            bl.stds[k] = round(new_std, 2)

        return bl

    def compute_z_scores(
        self, operator_id: str, features: BehaviourFeatures
    ) -> Dict[str, float]:
        """Compute standard z-scores for features against operator's baseline."""
        bl = self.get_or_create_baseline(operator_id)
        z_scores = {}

        feat_dict = {
            "mean_speed_mps": features.mean_speed_mps,
            "max_speed_mps": features.max_speed_mps,
            "mean_rpm": features.mean_rpm,
            "mean_fuel_rate_lph": features.mean_fuel_rate_lph,
            "idle_ratio": features.idle_ratio,
            "mean_fatigue": features.mean_fatigue,
            "seatbelt_compliance_pct": features.seatbelt_compliance_pct,
            "aggressive_maneuver_count": float(features.aggressive_maneuver_count),
            "unsafe_speed_events": float(features.unsafe_speed_events),
            "cycle_consistency_pct": features.cycle_consistency_pct,
        }

        for k, val in feat_dict.items():
            mean = bl.means.get(k, val)
            std = max(0.001, bl.stds.get(k, 1.0))
            z_scores[k] = round((val - mean) / std, 2)

        return z_scores

    def detect_signals(
        self, operator_id: str, features: BehaviourFeatures
    ) -> List[BehaviourSignal]:
        """Identify features deviating significantly (|z| >= 2.0) from baseline."""
        bl = self.get_or_create_baseline(operator_id)
        z_scores = self.compute_z_scores(operator_id, features)
        signals: List[BehaviourSignal] = []
        now = datetime.now(timezone.utc)
        ts_str = int(now.timestamp())

        for feature_name, z in z_scores.items():
            if abs(z) >= 2.0:
                mean = bl.means.get(feature_name, 0.0)
                std = bl.stds.get(feature_name, 1.0)
                observed = getattr(features, feature_name, 0.0)
                trend = TrendDirection.DEGRADING if z > 2.0 else TrendDirection.IMPROVING
                if feature_name in ("seatbelt_compliance_pct", "cycle_consistency_pct"):
                    trend = TrendDirection.DEGRADING if z < -2.0 else TrendDirection.IMPROVING

                signals.append(
                    BehaviourSignal(
                        signal_id=f"SIG-BEHAV-{operator_id}-{feature_name}-{ts_str}",
                        operator_id=operator_id,
                        timestamp=now,
                        signal_type=SignalType.BEHAVIOUR_FLAG,
                        feature_name=feature_name,
                        observed_value=float(observed),
                        baseline_mean=mean,
                        baseline_std=std,
                        z_score=z,
                        trend=trend,
                        description=(
                            f"Statistical outlier on {feature_name}: observed {observed}, baseline {mean:.1f}±{std:.1f} (z={z:.1f})"
                        ),
                    )
                )

        return signals
