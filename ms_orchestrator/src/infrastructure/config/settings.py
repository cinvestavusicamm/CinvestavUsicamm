from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Service Identification
    SERVICE_NAME: str = "ms_orchestrator"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Orchestrator Settings
    ORCHESTRATOR_HOST: str = "0.0.0.0"
    ORCHESTRATOR_PORT: int = 8000
    ORCHESTRATOR_WORKERS: int = 4

    # Microservices URLs
    VALIDATION_SERVICE_URL: str = "http://localhost:8001"
    BACKEND_API_URL: str = "http://localhost:8003"
    MICROSERVICE_DB_URL: str = "http://localhost:8002"
    DJANGO_BACKEND_URL: str = "http://localhost:8000"

    # Service timeouts (seconds)
    SERVICE_TIMEOUT: int = 30
    SERVICE_CONNECT_TIMEOUT: int = 10

    # Retry Settings
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_INITIAL_DELAY: float = 1.0

    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    ENABLE_REQUEST_LOGGING: bool = True
    ENABLE_RESPONSE_LOGGING: bool = True

    # CORS Settings
    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Security Settings
    API_KEY_HEADER: str = "X-API-Key"
    ENABLE_API_KEY_VALIDATION: bool = False
    VALID_API_KEYS: List[str] = []

    class Config:
        env_file = ".env.local"
        case_sensitive = True


settings = Settings()
