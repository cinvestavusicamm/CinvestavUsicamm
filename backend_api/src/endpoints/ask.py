from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from application.use_cases.agent.chat_rag import ChatRAGUseCase
from infrastructure.api.dependencies import get_chat_use_case
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    query: str

class ChatRequestStream(BaseModel):
    prompt: str  # Para compatibilidad con agent_ajax.py

@router.post("/ask")
async def ask_agent(
    request: ChatRequest,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    """Endpoint para chat normal"""
    try:
        response = await use_case.run(request.query)
        return {"response": response}
    except Exception as e:
        logger.exception(f"Error en ask_agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask/stream")
async def ask_agent_streaming(
    request: Request,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    """Endpoint para streaming"""
    try:
        # Leer el JSON de la petición
        data = await request.json()
        query = data.get("query") or data.get("prompt") or ""
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "No se proporcionó query"}
            )
        
        async def generate():
            try:
                # Usar el nuevo método streaming del use case
                async for chunk in use_case.run_streaming(query):
                    # Enviar cada chunk como evento SSE
                    yield f"data: {json.dumps({'token': chunk})}\n\n"
                
                # Marcar finalización
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.exception(f"Error en streaming: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
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