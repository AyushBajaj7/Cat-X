"""API Gateway configuration module."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    """Runtime configuration for API Gateway."""

    model_config = SettingsConfigDict(env_prefix="GATEWAY_")

    service_name: str = "api-gateway"
    service_port: int = 8000
    env: str = os.getenv("ENV", "development")
    safety_service_url: str = os.getenv("SAFETY_SERVICE_URL", "http://localhost:8001")
    operations_service_url: str = os.getenv("OPERATIONS_SERVICE_URL", "http://localhost:8002")
    training_service_url: str = os.getenv("TRAINING_SERVICE_URL", "http://localhost:8003")


settings = GatewaySettings()
