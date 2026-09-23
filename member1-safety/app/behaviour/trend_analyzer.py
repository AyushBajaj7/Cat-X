"""Multi-axis behavioural trend analyzer.

NOTE: Operational trends are evaluated along distinct, orthogonal behavioral
axes (Fatigue, Speed Control, Seatbelt Compliance, and Idle Efficiency).
No single 'composite operator quality score' is used to collapse these dimensions.
"""

from dataclasses import dataclass
from typing import Dict, List
from ..models import TrendDirection
from .features import BehaviourFeatures


@dataclass
class OperatorTrends:
    """Distinct multi-axis behavioral trends."""

    fatigue_trend: TrendDirection
    speed_control_trend: TrendDirection
    seatbelt_compliance_trend: TrendDirection
    idle_efficiency_trend: TrendDirection

    def to_dict(self) -> Dict[str, TrendDirection]:
        return {
            "fatigue": self.fatigue_trend,
            "speed_control": self.speed_control_trend,
            "seatbelt_compliance": self.seatbelt_compliance_trend,
            "idle_efficiency": self.idle_efficiency_trend,
        }


class TrendAnalyzer:
    """
    Computes trajectory direction along independent behavioral axes by comparing
    recent window feature sets against earlier baseline windows.
    """

    def __init__(self):
        # operator_id -> list of historical BehaviourFeatures
        self._history: Dict[str, List[BehaviourFeatures]] = {}

    def record_snapshot(self, operator_id: str, features: BehaviourFeatures):
        if operator_id not in self._history:
            self._history[operator_id] = []
        self._history[operator_id].append(features)
        # Keep last 20 snapshots
        if len(self._history[operator_id]) > 20:
            self._history[operator_id] = self._history[operator_id][-20:]

    def analyze_trends(self, operator_id: str) -> OperatorTrends:
        snapshots = self._history.get(operator_id, [])
        if len(snapshots) < 2:
            return OperatorTrends(
                fatigue_trend=TrendDirection.STABLE,
                speed_control_trend=TrendDirection.STABLE,
                seatbelt_compliance_trend=TrendDirection.STABLE,
                idle_efficiency_trend=TrendDirection.STABLE,
            )

        mid = len(snapshots) // 2
        older = snapshots[:mid]
        recent = snapshots[mid:]

        # 1. Fatigue Trend (Higher fatigue = DEGRADING)
        old_fatigue = sum(s.mean_fatigue for s in older) / len(older)
        rec_fatigue = sum(s.mean_fatigue for s in recent) / len(recent)
        fatigue_diff = rec_fatigue - old_fatigue
        if fatigue_diff > 5.0:
            fatigue_trend = TrendDirection.DEGRADING
        elif fatigue_diff < -5.0:
            fatigue_trend = TrendDirection.IMPROVING
        else:
            fatigue_trend = TrendDirection.STABLE

        # 2. Speed Control Trend (Higher aggressive maneuvers or unsafe speed = DEGRADING)
        old_agg = sum(s.aggressive_maneuver_count + s.unsafe_speed_events for s in older) / len(older)
        rec_agg = sum(s.aggressive_maneuver_count + s.unsafe_speed_events for s in recent) / len(recent)
        if rec_agg > old_agg + 0.3:
            speed_trend = TrendDirection.DEGRADING
        elif rec_agg < old_agg - 0.3:
            speed_trend = TrendDirection.IMPROVING
        else:
            speed_trend = TrendDirection.STABLE

        # 3. Seatbelt Compliance Trend (Lower compliance = DEGRADING)
        old_sb = sum(s.seatbelt_compliance_pct for s in older) / len(older)
        rec_sb = sum(s.seatbelt_compliance_pct for s in recent) / len(recent)
        sb_diff = rec_sb - old_sb
        if sb_diff < -3.0:
            sb_trend = TrendDirection.DEGRADING
        elif sb_diff > 3.0:
            sb_trend = TrendDirection.IMPROVING
        else:
            sb_trend = TrendDirection.STABLE

        # 4. Idle Efficiency Trend (Higher idle ratio = DEGRADING efficiency)
        old_idle = sum(s.idle_ratio for s in older) / len(older)
        rec_idle = sum(s.idle_ratio for s in recent) / len(recent)
        idle_diff = rec_idle - old_idle
        if idle_diff > 0.08:
            idle_trend = TrendDirection.DEGRADING
        elif idle_diff < -0.08:
            idle_trend = TrendDirection.IMPROVING
        else:
            idle_trend = TrendDirection.STABLE

        return OperatorTrends(
            fatigue_trend=fatigue_trend,
            speed_control_trend=speed_trend,
            seatbelt_compliance_trend=sb_trend,
            idle_efficiency_trend=idle_trend,
        )
