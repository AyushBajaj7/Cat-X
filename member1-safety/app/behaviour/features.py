"""Feature extraction from rolling telemetry events for behavioral modeling."""

from dataclasses import dataclass
from typing import List
import numpy as np
from ..models import TelemetryEventInput


@dataclass
class BehaviourFeatures:
    """Extracted behavioral metrics and multivariate feature vector."""

    mean_speed_mps: float
    max_speed_mps: float
    speed_variance: float
    mean_rpm: float
    mean_fuel_rate_lph: float
    idle_ratio: float  # 0.0 - 1.0 fraction of events stationary/idle
    mean_fatigue: float
    max_fatigue: float
    seatbelt_compliance_pct: float
    aggressive_maneuver_count: int
    unsafe_speed_events: int
    cycle_consistency_pct: float

    def to_feature_vector(self) -> List[float]:
        """Vector representation for scikit-learn anomaly scoring."""
        return [
            self.mean_speed_mps,
            self.max_speed_mps,
            self.speed_variance,
            self.mean_rpm,
            self.mean_fuel_rate_lph,
            self.idle_ratio,
            self.mean_fatigue,
            self.max_fatigue,
            self.seatbelt_compliance_pct,
            float(self.aggressive_maneuver_count),
            float(self.unsafe_speed_events),
            self.cycle_consistency_pct,
        ]


class FeatureExtractor:
    """Extracts multivariate behavioral metrics from a sequence of telemetry events."""

    @staticmethod
    def extract_features(events: List[TelemetryEventInput]) -> BehaviourFeatures:
        if not events:
            # Return nominal default baseline features
            return BehaviourFeatures(
                mean_speed_mps=1.5,
                max_speed_mps=3.2,
                speed_variance=0.8,
                mean_rpm=1750.0,
                mean_fuel_rate_lph=16.0,
                idle_ratio=0.12,
                mean_fatigue=22.0,
                max_fatigue=30.0,
                seatbelt_compliance_pct=98.0,
                aggressive_maneuver_count=0,
                unsafe_speed_events=0,
                cycle_consistency_pct=92.0,
            )

        speeds: List[float] = []
        rpms: List[float] = []
        fuel_rates: List[float] = []
        fatigues: List[float] = []
        buckled_count = 0
        idle_count = 0
        aggressive_count = 0
        unsafe_speed_count = 0

        prev_speed = None
        prev_rpm = None

        for evt in events:
            # Speed in mps
            sp = evt.machine_speed_mps
            if sp is None:
                sp = round(evt.machine.speed_kmh / 3.6, 3)
            speeds.append(sp)

            rpm = evt.machine.engine_rpm
            rpms.append(rpm)

            fr = evt.fuel_rate_lph or evt.machine.fuel_rate_lph or 15.0
            fuel_rates.append(fr)

            fatigues.append(evt.operator.fatigue_score)

            sb_status = evt.seatbelt_status or ("BUCKLED" if evt.operator.seatbelt_fastened else "UNBUCKLED")
            if sb_status == "BUCKLED":
                buckled_count += 1

            if sp < 0.2:
                idle_count += 1

            if sp > 8.33:  # > 30 km/h
                unsafe_speed_count += 1

            # Detect aggressive maneuvers (abrupt jerk or throttle transitions)
            if prev_speed is not None:
                delta_speed = abs(sp - prev_speed)
                if delta_speed > 2.5:  # Rapid acceleration/deceleration > 2.5 m/s delta
                    aggressive_count += 1
            if prev_rpm is not None:
                delta_rpm = abs(rpm - prev_rpm)
                if delta_rpm > 800.0:  # Rapid throttle punch
                    aggressive_count += 1

            prev_speed = sp
            prev_rpm = rpm

        n = len(events)
        mean_speed = float(np.mean(speeds))
        max_speed = float(np.max(speeds))
        speed_var = float(np.var(speeds))
        mean_rpm = float(np.mean(rpms))
        mean_fuel = float(np.mean(fuel_rates))
        idle_ratio = round(idle_count / n, 3)
        mean_fatigue = float(np.mean(fatigues))
        max_fatigue = float(np.max(fatigues))
        compliance_pct = round((buckled_count / n) * 100.0, 1)

        # Consistency metric based on coefficient of variation of work cycle metrics
        cv = (np.std(speeds) / (mean_speed + 0.1)) if mean_speed > 0 else 0.5
        cycle_consistency = max(50.0, min(100.0, round(100.0 - (cv * 30.0), 1)))

        return BehaviourFeatures(
            mean_speed_mps=round(mean_speed, 2),
            max_speed_mps=round(max_speed, 2),
            speed_variance=round(speed_var, 3),
            mean_rpm=round(mean_rpm, 1),
            mean_fuel_rate_lph=round(mean_fuel, 2),
            idle_ratio=idle_ratio,
            mean_fatigue=round(mean_fatigue, 1),
            max_fatigue=round(max_fatigue, 1),
            seatbelt_compliance_pct=compliance_pct,
            aggressive_maneuver_count=aggressive_count,
            unsafe_speed_events=unsafe_speed_count,
            cycle_consistency_pct=cycle_consistency,
        )
