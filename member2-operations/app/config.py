"""Operations Service configuration module."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class OperationsSettings(BaseSettings):
    """Runtime configuration for Operations Service."""

    model_config = SettingsConfigDict(env_prefix="OPERATIONS_")

    service_name: str = "operations-service"
    service_port: int = 8002
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cat_admin:cat_secure_password_2026@localhost:5432/cat_shift_twin"
    )
    safety_service_url: str = os.getenv("SAFETY_SERVICE_URL", "http://localhost:8001")


settings = OperationsSettings()
