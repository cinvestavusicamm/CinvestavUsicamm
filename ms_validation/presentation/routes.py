"""ms_validation.presentation.routes

FastAPI router exposing the validation endpoint.

Concurrency guard:
  A global asyncio.Semaphore(1) protects the 6 GB VRAM of Phi-3.
  If the semaphore cannot be acquired within SEMAPHORE_TIMEOUT seconds
  the endpoint returns HTTP 429 (Too Many Requests) instead of queuing
  indefinitely and risking OOM.

Error handling:
  - LLMOutputParseError  →  HTTP 502 (Bad Gateway) with diagnostic hint.
  - VRAMBusyError        →  HTTP 429 (Too Many Requests).
  - Unexpected errors    →  HTTP 500 with generic message.
"""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from ms_validation.application.validate_process import ValidateProcessUseCase
from ms_validation.domain.exceptions import LLMOutputParseError, VRAMBusyError
from ms_validation.domain.schemas import (
    ProcessInput,
    ValidationResponse,
)
from ms_validation.infrastructure.config import settings
from ms_validation.infrastructure.dependencies import (
    get_validate_use_case,
    phi_semaphore,
)

logger = logging.getLogger("ms_validation.api")

router = APIRouter()


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="Valida un proceso contra las reglas de negocio",
    responses={
        429: {"description": "LLM ocupado — reintente en unos segundos."},
        502: {"description": "El LLM devolvió una respuesta no parseable."},
    },
)
async def validate_process(payload: ProcessInput) -> ValidationResponse:
    """
    Recibe la descripción del proceso propuesto y la evalúa contra
    la normativa almacenada en Qdrant mediante RAG.
    """

    use_case: ValidateProcessUseCase = get_validate_use_case()

    # ── Acquire VRAM semaphore with timeout ──
    try:
        await asyncio.wait_for(
            phi_semaphore.acquire(), timeout=settings.SEMAPHORE_TIMEOUT
        )
    except asyncio.TimeoutError:
        logger.warning(
            "Semaphore timeout for process %s — returning 429",
            payload.process_id,
        )
        raise HTTPException(
            status_code=429,
            detail=(
                "El modelo de IA está procesando otra solicitud. "
                "Reintente en unos segundos."
            ),
        )

    try:
        result = await use_case.execute(payload)
        return result

    except LLMOutputParseError as exc:
        logger.error(
            "LLM parse error for process %s: %s",
            payload.process_id,
            exc,
        )
        raise HTTPException(
            status_code=502,
            detail={
                "error": "LLM output could not be parsed into the required validation schema.",
                "raw_hint": exc.raw_output[:200],
                "reason": exc.reason,
            },
        )

    except Exception as exc:
        logger.exception("Unexpected error validating process %s", payload.process_id)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servicio de validación.",
        )

    finally:
        phi_semaphore.release()
