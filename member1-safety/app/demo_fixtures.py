"""Deterministic demo fixtures for CAT Operator Shift Twin evaluation.

These 6 scenarios showcase the end-to-end intelligence of Engineer 1's domain:
1. NORMAL_OPERATION: Compliant operator, nominal speed, clear envelope.
2. UNBUCKLED_TRAMMING: Unbuckled operator moving at tramming speed (> 2 m/s).
3. CRITICAL_PROXIMITY: Severe proximity incursion (< 5m) triggering collision hold.
4. COMBINED_HAZARD: Correlated concurrent unbuckled + proximity breach.
5. EXCESSIVE_IDLE: 52-minute stationary engine run generating fuel waste metrics.
6. BEHAVIOURAL_DRIFT: Multi-event sequence showing escalating fatigue and erratic maneuvers.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from .models import (
    EnvironmentTelemetry,
    MachineTelemetry,
    OperatorTelemetry,
    TelemetryEventInput,
)


def get_normal_operation_event(
    operator_id: str = "OP-NORM-01", machine_id: str = "EXC-CAT-349"
) -> TelemetryEventInput:
    """Fixture 1: Safe and productive baseline operation."""
    now = datetime.now(timezone.utc)
    return TelemetryEventInput(
        event_id=f"EVT-NORM-{int(now.timestamp())}",
        timestamp=now,
        machine_id=machine_id,
        operator_id=operator_id,
        task_id="TASK-TRENCH-A1",
        machine=MachineTelemetry(
            engine_rpm=1750.0,
            engine_temp_c=86.0,
            hydraulic_pressure_kpa=23500.0,
            fuel_rate_lph=16.2,
            speed_kmh=5.4,  # ~1.5 m/s
            operating_hours=1420.5,
        ),
        operator=OperatorTelemetry(
            seatbelt_fastened=True,
            fatigue_score=18.0,
            heart_rate_bpm=74,
            continuous_hours=1.8,
        ),
        environment=EnvironmentTelemetry(
            weather_condition="CLEAR",
            ambient_temp_c=22.5,
            ground_saturation_pct=15.0,
        ),
        engine_hours=1420.5,
        fuel_used_l=82.0,
        load_cycles=42,
        idle_minutes=4.5,
        seatbelt_status="BUCKLED",
        proximity_distance_m=42.0,
        machine_state="WORKING",
        machine_speed_mps=1.5,
        fuel_rate_lph=16.2,
    )


def get_unbuckled_tramming_event(
    operator_id: str = "OP-UNBUCK-02", machine_id: str = "EXC-CAT-349"
) -> TelemetryEventInput:
    """Fixture 2: Operator unbuckled during high-speed transit/tramming."""
    now = datetime.now(timezone.utc)
    return TelemetryEventInput(
        event_id=f"EVT-UNBUCK-{int(now.timestamp())}",
        timestamp=now,
        machine_id=machine_id,
        operator_id=operator_id,
        task_id="TASK-BENCH-TRANSIT",
        machine=MachineTelemetry(
            engine_rpm=1950.0,
            engine_temp_c=89.0,
            hydraulic_pressure_kpa=18000.0,
            fuel_rate_lph=22.5,
            speed_kmh=11.5,  # ~3.2 m/s
            operating_hours=1421.2,
        ),
        operator=OperatorTelemetry(
            seatbelt_fastened=False,
            fatigue_score=24.0,
            heart_rate_bpm=82,
            continuous_hours=2.5,
        ),
        environment=EnvironmentTelemetry(
            weather_condition="CLEAR",
            ambient_temp_c=23.0,
            ground_saturation_pct=10.0,
        ),
        engine_hours=1421.2,
        fuel_used_l=98.5,
        load_cycles=42,
        idle_minutes=6.0,
        seatbelt_status="UNBUCKLED",
        proximity_distance_m=35.0,
        machine_state="TRAMMING",
        machine_speed_mps=3.2,
        fuel_rate_lph=22.5,
    )


def get_critical_proximity_event(
    operator_id: str = "OP-PROX-03", machine_id: str = "EXC-CAT-349"
) -> TelemetryEventInput:
    """Fixture 3: Critical proximity incursion (< 5m) requiring immediate hold."""
    now = datetime.now(timezone.utc)
    return TelemetryEventInput(
        event_id=f"EVT-PROX-{int(now.timestamp())}",
        timestamp=now,
        machine_id=machine_id,
        operator_id=operator_id,
        task_id="TASK-TRUCK-LOAD-B",
        machine=MachineTelemetry(
            engine_rpm=1820.0,
            engine_temp_c=87.0,
            hydraulic_pressure_kpa=25000.0,
            fuel_rate_lph=18.0,
            speed_kmh=4.0,  # ~1.1 m/s
            operating_hours=1422.0,
        ),
        operator=OperatorTelemetry(
            seatbelt_fastened=True,
            fatigue_score=35.0,
            heart_rate_bpm=88,
            continuous_hours=3.2,
        ),
        environment=EnvironmentTelemetry(
            weather_condition="FOG",
            ambient_temp_c=18.0,
            ground_saturation_pct=25.0,
            visibility_meters=150.0,
        ),
        engine_hours=1422.0,
        fuel_used_l=112.0,
        load_cycles=55,
        idle_minutes=8.0,
        seatbelt_status="BUCKLED",
        proximity_distance_m=3.4,  # Critical breach!
        machine_state="WORKING",
        machine_speed_mps=1.1,
        fuel_rate_lph=18.0,
    )


def get_combined_hazard_event(
    operator_id: str = "OP-COMBO-04", machine_id: str = "EXC-CAT-349"
) -> TelemetryEventInput:
    """Fixture 4: Concurrent unbuckled operator + proximity breach."""
    now = datetime.now(timezone.utc)
    return TelemetryEventInput(
        event_id=f"EVT-COMBO-{int(now.timestamp())}",
        timestamp=now,
        machine_id=machine_id,
        operator_id=operator_id,
        task_id="TASK-PIT-WALL-CLEAR",
        machine=MachineTelemetry(
            engine_rpm=1880.0,
            engine_temp_c=91.0,
            hydraulic_pressure_kpa=24200.0,
            fuel_rate_lph=19.4,
            speed_kmh=6.5,  # ~1.8 m/s
            operating_hours=1423.5,
        ),
        operator=OperatorTelemetry(
            seatbelt_fastened=False,  # Unbuckled
            fatigue_score=68.0,
            heart_rate_bpm=94,
            continuous_hours=4.8,
        ),
        environment=EnvironmentTelemetry(
            weather_condition="RAIN",
            ambient_temp_c=16.0,
            ground_saturation_pct=65.0,
            visibility_meters=400.0,
        ),
        engine_hours=1423.5,
        fuel_used_l=145.0,
        load_cycles=68,
        idle_minutes=12.0,
        seatbelt_status="UNBUCKLED",
        proximity_distance_m=7.2,  # Close proximity hazard
        machine_state="WORKING",
        machine_speed_mps=1.8,
        fuel_rate_lph=19.4,
    )


def get_excessive_idle_event(
    operator_id: str = "OP-IDLE-05", machine_id: str = "EXC-CAT-349"
) -> TelemetryEventInput:
    """Fixture 5: 52-minute stationary engine run for fuel waste intelligence."""
    now = datetime.now(timezone.utc)
    return TelemetryEventInput(
        event_id=f"EVT-IDLE-{int(now.timestamp())}",
        timestamp=now,
        machine_id=machine_id,
        operator_id=operator_id,
        task_id="TASK-QUEUE-CRUSHER",
        machine=MachineTelemetry(
            engine_rpm=820.0,  # Low idle
            engine_temp_c=78.0,
            hydraulic_pressure_kpa=3200.0,
            fuel_rate_lph=14.5,
            speed_kmh=0.0,
            operating_hours=1424.8,
        ),
        operator=OperatorTelemetry(
            seatbelt_fastened=True,
            fatigue_score=42.0,
            heart_rate_bpm=66,
            continuous_hours=5.5,
        ),
        environment=EnvironmentTelemetry(
            weather_condition="CLEAR",
            ambient_temp_c=28.0,
            ground_saturation_pct=5.0,
        ),
        engine_hours=1424.8,
        fuel_used_l=165.0,
        load_cycles=72,
        idle_minutes=52.0,  # Critical idle breach > 45 min
        seatbelt_status="BUCKLED",
        proximity_distance_m=28.0,
        machine_state="IDLE",
        machine_speed_mps=0.0,
        fuel_rate_lph=14.5,
    )


def get_behavioural_drift_sequence(
    operator_id: str = "OP-DRIFT-06", machine_id: str = "EXC-CAT-349"
) -> List[TelemetryEventInput]:
    """
    Fixture 6: Sequence of 15 telemetry events exhibiting progressive behavioral
    degradation: rising fatigue, aggressive throttle transitions, and lower compliance.
    """
    base_time = datetime.now(timezone.utc) - timedelta(minutes=45)
    sequence: List[TelemetryEventInput] = []

    for i in range(15):
        event_time = base_time + timedelta(minutes=i * 3)
        # Fatigue steadily climbs from 30 to 86
        fatigue = min(92.0, 30.0 + (i * 4.0))
        # Erratic speed adjustments and unbuckling towards the end
        speed_mps = 1.2 if i < 8 else (3.8 if i % 2 == 0 else 0.4)
        rpm = 1750.0 if i < 8 else (2300.0 if i % 2 == 0 else 800.0)
        seatbelt = True if i < 11 else False

        evt = TelemetryEventInput(
            event_id=f"EVT-DRIFT-{operator_id}-{i:03d}",
            timestamp=event_time,
            machine_id=machine_id,
            operator_id=operator_id,
            task_id="TASK-OVERBURDEN-NIGHT",
            machine=MachineTelemetry(
                engine_rpm=rpm,
                engine_temp_c=85.0 + (i * 0.5),
                hydraulic_pressure_kpa=22000.0 + (i * 300),
                fuel_rate_lph=16.0 + (i * 0.6),
                speed_kmh=round(speed_mps * 3.6, 1),
                operating_hours=1425.0 + (i * 0.05),
            ),
            operator=OperatorTelemetry(
                seatbelt_fastened=seatbelt,
                fatigue_score=round(fatigue, 1),
                continuous_hours=round(3.0 + (i * 0.25), 1),
            ),
            environment=EnvironmentTelemetry(
                weather_condition="CLEAR",
                ambient_temp_c=19.0,
                ground_saturation_pct=12.0,
            ),
            engine_hours=round(1425.0 + (i * 0.05), 2),
            fuel_used_l=round(170.0 + (i * 1.5), 1),
            load_cycles=80 + (i // 2),
            idle_minutes=round(2.0 + (i * 1.2), 1),
            seatbelt_status="BUCKLED" if seatbelt else "UNBUCKLED",
            proximity_distance_m=18.0 if i < 10 else 8.5,
            machine_state="WORKING" if speed_mps > 0 else "IDLE",
            machine_speed_mps=speed_mps,
            fuel_rate_lph=round(16.0 + (i * 0.6), 1),
        )
        sequence.append(evt)

    return sequence


ALL_FIXTURES: Dict[str, Any] = {
    "NORMAL_OPERATION": get_normal_operation_event,
    "UNBUCKLED_TRAMMING": get_unbuckled_tramming_event,
    "CRITICAL_PROXIMITY": get_critical_proximity_event,
    "COMBINED_HAZARD": get_combined_hazard_event,
    "EXCESSIVE_IDLE": get_excessive_idle_event,
    "BEHAVIOURAL_DRIFT": get_behavioural_drift_sequence,
}
