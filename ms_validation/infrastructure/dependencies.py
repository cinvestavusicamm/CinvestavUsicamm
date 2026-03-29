"""ms_validation.infrastructure.dependencies

Composition Root — manual dependency injection.

This module wires together all adapters and use cases.
It also creates the global asyncio.Semaphore(1) that protects the
6 GB VRAM of the Phi-3 model from concurrent requests.
"""

import asyncio

from ms_validation.application.validate_process import ValidateProcessUseCase
from ms_validation.application.ingest_rules import IngestRulesUseCase
from ms_validation.infrastructure.adapters.ollama_llm import OllamaLLMAdapter
from ms_validation.infrastructure.adapters.qdrant_vector_repo import QdrantVectorRepo
from ms_validation.infrastructure.config import settings

# ──────────────────────────────────────────────
# Concrete adapter instances
# ──────────────────────────────────────────────

vector_repo = QdrantVectorRepo(
    url=settings.QDRANT_URL,
    collection_name=settings.QDRANT_COLLECTION,
)

llm_service = OllamaLLMAdapter(
    base_url=settings.OLLAMA_BASE_URL,
    llm_model=settings.LLM_MODEL,
    embed_model=settings.EMBEDDING_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    timeout=settings.LLM_TIMEOUT,
)

# ──────────────────────────────────────────────
# VRAM protection — single-slot semaphore
# ──────────────────────────────────────────────

phi_semaphore: asyncio.Semaphore = asyncio.Semaphore(1)

# ──────────────────────────────────────────────
# Use case factories
# ──────────────────────────────────────────────

def get_validate_use_case() -> ValidateProcessUseCase:
    """Factory that provides a fully-wired ValidateProcessUseCase."""
    return ValidateProcessUseCase(
        vector_repo=vector_repo,
        llm_service=llm_service,
        rag_top_k=settings.RAG_TOP_K,
    )

def get_ingest_use_case() -> IngestRulesUseCase:
    """Factory that provides a fully-wired IngestRulesUseCase for PDF parsing."""
    return IngestRulesUseCase(
        vector_repo=vector_repo,
        llm_service=llm_service,
        chunk_size=800,
        chunk_overlap=150,
    )
