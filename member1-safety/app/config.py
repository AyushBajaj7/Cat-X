"""Safety Service configuration module."""

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
        "postgresql://cat_admin:cat_secure_password_2026@localhost:5432/cat_shift_twin"
    )


settings = SafetySettings()
