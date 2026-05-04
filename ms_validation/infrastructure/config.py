"""ms_validation.infrastructure.config

Centralised settings loaded from environment variables with safe defaults.
"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for ms_validation. Every value can be overridden via env var."""

    # ── Ollama / LLM ──
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://motor_ollama:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "phi3:mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # ── Qdrant ──
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://qdrant:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "ms_validation_rules")

    # ── RAG ──
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))

    # ── Semaphore timeout (seconds) before returning HTTP 429 ──
    SEMAPHORE_TIMEOUT: float = float(os.getenv("SEMAPHORE_TIMEOUT", "30.0"))

    # ── LLM generation-specific ──
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "120.0"))


settings = Settings()
