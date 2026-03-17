from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from application.use_cases.agent.chat_rag import ChatRAGUseCase
from infrastructure.api.dependencies import get_chat_use_case
import json
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

@router.post("/ask", response_model=ChatResponse)
async def ask_agent(
    request: ChatRequest,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    """Endpoint para chat normal (sin streaming)"""
    try:
        logger.info(f"Recibida consulta: {request.prompt[:50]}...")
        response = await use_case.run(request.prompt)
        return {"response": response}
    except Exception as e:
        logger.exception(f"Error en ask_agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask/stream")
async def ask_agent_streaming(
    request: Request,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    """Endpoint para streaming con mejor formato"""
    try:
        data = await request.json()
        prompt = data.get("prompt") or data.get("query") or ""
        
        if not prompt:
            return JSONResponse(
                status_code=400,
                content={"error": "No se proporcionó prompt"}
            )
        
        logger.info(f"Streaming request: {prompt[:50]}...")
        
        async def generate():
            try:
                # Enviar un mensaje inicial para mejor experiencia
                await asyncio.sleep(0.1)  # Pequeña pausa para efecto natural
                
                # Usar el método streaming del use case
                async for chunk in use_case.run_streaming(prompt):
                    if chunk and chunk.strip():  # Solo enviar chunks no vacíos
                        # Formato más limpio para el frontend
                        yield f"data: {json.dumps({'token': chunk, 'type': 'content'})}\n\n"
                
                # Mensaje de finalización
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                logger.exception(f"Error en streaming: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.exception(f"Error en ask_agent_streaming: {e}")
        raise HTTPException(status_code=500, detail=str(e))