import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de Datos
    DB_USER: str = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME: str = os.getenv("POSTGRES_DB", "Escalafon_db")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://motor_ollama:11434")
    LLM_MODEL: str = "llama3:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text"

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()