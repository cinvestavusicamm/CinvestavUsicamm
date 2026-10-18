import json
import logging
import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.application.use_cases.chat_rag import ChatRAGUseCase
from src.domain.exceptions import IAError
from src.infrastructure.api.dependencies import get_chat_use_case
from src.infrastructure.api.security import verify_internal_key

logger = logging.getLogger(__name__)

router = APIRouter()


def error_ia(excepcion: Exception) -> HTTPException:
    """Traduce un fallo de la IA a un codigo HTTP, sin filtrar el detalle.

    Antes cualquier fallo se devolvia como 500 con `str(e)`, que llevaba dentro
    la URL de Ollama y a veces el texto del modelo. El detalle se queda en el
    log; al consumidor le llega el codigo y un mensaje corto.
    """
    if isinstance(excepcion, httpx.TimeoutException):
        return HTTPException(status_code=504, detail="La IA tardo demasiado")
    if isinstance(excepcion, httpx.ConnectError):
        return HTTPException(status_code=503, detail="No se pudo contactar con la IA")
    if isinstance(excepcion, IAError):
        return HTTPException(status_code=502, detail="La IA no pudo generar la respuesta")
    return HTTPException(status_code=500, detail="Error inesperado en el servicio de IA")


class ChatRequest(BaseModel):
    query: str
    role: str = "teacher"
    user_id: str = "anon"


class StreamRequest(BaseModel):
    prompt: str


@router.post("/ask", dependencies=[Depends(verify_internal_key)])
async def ask_agent(
    request: ChatRequest,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    try:
        response_text = await use_case.run(request.query, user_role=request.role)

        return {
            "response": response_text,
            "meta": {
                "processed_by": "ia_service_core",
                "role_applied": request.role,
                "user_audit": request.user_id
            }
        }

    except Exception as e:
        logger.exception("Error en /ask")
        raise error_ia(e)


@router.post("/ask/stream", dependencies=[Depends(verify_internal_key)])
async def ask_agent_stream(
    request: StreamRequest,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    """Endpoint de streaming para chatbots"""
    async def generate():
        try:
            response_text = await use_case.run(request.prompt, user_role="teacher")

            # Enviar la respuesta token por token
            for char in response_text:
                yield f"data: {json.dumps({'type': 'content', 'token': char})}\n\n"
                await asyncio.sleep(0.01)  # Pequeño delay para efecto de streaming

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            # El detalle va al log; al stream solo un mensaje que el navegador
            # pueda mostrar. Antes salia str(e), con la URL interna dentro.
            logger.exception("Error en /ask/stream")
            yield f"data: {json.dumps({'type': 'error', 'error': 'La IA no pudo generar la respuesta'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
