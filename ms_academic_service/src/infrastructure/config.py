from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    SERVICE_NAME: str = "ms_academic_service"
    SERVICE_TITLE: str = "Academic Service"
    SERVICE_DESCRIPTION: str = "Servicio acadÃ©mico: alumnos, profesores, grupos, materias y turnos."
    SERVICE_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    CORS_ALLOW_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    JWT_SECRET: str = "replace-with-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    AUTH_SERVICE_URL: str = "http://ms_auth_service:8101"
    ACADEMIC_SERVICE_URL: str = "http://ms_academic_service:8102"
    ASSESSMENT_SERVICE_URL: str = "http://ms_assessment_service:8103"
    COURSE_SERVICE_URL: str = "http://ms_course_service:8104"
    ADMIN_SERVICE_URL: str = "http://ms_admin_service:8105"
    NOTIFICATION_SERVICE_URL: str = "http://ms_notification_service:8106"
    AI_AGENT_SERVICE_URL: str = "http://ms_ai_agent_service:8107"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


settings = Settings()
