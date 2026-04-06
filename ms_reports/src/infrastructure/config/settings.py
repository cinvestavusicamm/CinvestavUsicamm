"""infrastructure.config.settings

Configuraciones del microservicio de Reportes.
Usa pydantic_settings para leer automáticamente del entorno y validar tipos.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API
    HOST: str = Field(default="0.0.0.0", alias="MS3_HOST")
    PORT: int = Field(default=8003, alias="MS3_PORT")
    REDIS_URL: str = Field(default="redis://redis_reports:6379", alias="MS3_REDIS_URL")
    
    # Almacenamiento de PDFs generados (MinIO / S3)
    S3_ENDPOINT: str = Field(default="http://minio:9000", alias="MS3_S3_ENDPOINT")
    S3_ACCESS_KEY: str = Field(default="minioadmin", alias="MS3_S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field(default="minioadmin", alias="MS3_S3_SECRET_KEY")
    S3_BUCKET: str = Field(default="reports", alias="MS3_S3_BUCKET")
    
    # Base de Datos Local Compartida (PostgreSQL)
    DATABASE_URL: str = Field(default="postgresql://dev:dev@db:5432/dev_db", alias="DATABASE_URL")

    # Infraestructura IA Unificada (Ollama + Qdrant)
    OLLAMA_BASE_URL: str = Field(default="http://172.20.0.1:11434")
    OLLAMA_LLM_MODEL: str = Field(default="phi3:mini")
    OLLAMA_EMBED_MODEL: str = Field(default="nomic-embed-text")
    
    QDRANT_URL: str = Field(default="http://qdrant:6333")
    QDRANT_COLLECTION: str = Field(default="ms_reports_styles")

    # Configuración del modelo: busca el archivo .env o lee las variables inyectadas por Docker
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()