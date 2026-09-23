"""Safety Service configuration module.

NOTE: All thresholds in this configuration are demo assumptions for hackathon
evaluation and should not be construed as Caterpillar official engineering
specifications.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class SafetySettings(BaseSettings):
    """Runtime configuration for Safety Service."""

    model_config = SettingsConfigDict(env_prefix="SAFETY_")

    service_name: str = "safety-service"
    service_port: int = 8001
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cat_admin:cat_secure_password_2026@localhost:5432/cat_shift_twin",
    )

    # Proximity thresholds (meters) - Demo assumptions
    proximity_critical_m: float = 5.0
    proximity_high_m: float = 10.0
    proximity_medium_m: float = 20.0
    proximity_low_m: float = 30.0

    # Speed thresholds (meters per second)
    speed_moving_threshold_mps: float = 0.5
    speed_tramming_threshold_mps: float = 2.0
    speed_overspeed_mps: float = 8.33  # ~30 km/h

    # Excessive idle thresholds (minutes) - Behaviour intelligence
    idle_warning_minutes: float = 25.0
    idle_critical_minutes: float = 45.0

    # Incident management
    incident_dedup_window_seconds: int = 300  # 5-minute deduplication window

    # Anomaly engine parameters
    anomaly_window_size: int = 50
    isolation_forest_contamination: float = 0.05
    isolation_forest_n_estimators: int = 50
    isolation_forest_random_state: int = 42

    # Fatigue score thresholds (0-100 scale)
    fatigue_warning_score: float = 70.0
    fatigue_critical_score: float = 85.0

    # Persistence settings
    db_auto_create: bool = True
    sqlite_fallback: bool = True
    sqlite_fallback_url: str = "sqlite:///./safety.db"


settings = SafetySettings()
