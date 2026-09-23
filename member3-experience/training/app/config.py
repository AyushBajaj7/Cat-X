"""Training Service configuration module."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class TrainingSettings(BaseSettings):
    """Runtime configuration for Training Service."""

    model_config = SettingsConfigDict(env_prefix="TRAINING_")

    service_name: str = "training-service"
    service_port: int = 8003
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cat_admin:cat_secure_password_2026@localhost:5432/cat_shift_twin"
    )


settings = TrainingSettings()
