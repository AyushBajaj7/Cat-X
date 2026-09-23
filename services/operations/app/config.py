"""Operations Service configuration module."""

import os
from pydantic_settings import BaseSettings


class OperationsSettings(BaseSettings):
    """Runtime configuration for Operations Service."""

    service_name: str = "operations-service"
    service_port: int = 8002
    env: str = os.getenv("ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cat_admin:cat_secure_password_2026@localhost:5432/cat_shift_twin"
    )
    safety_service_url: str = os.getenv("SAFETY_SERVICE_URL", "http://localhost:8001")

    class Config:
        env_prefix = "OPERATIONS_"


settings = OperationsSettings()
