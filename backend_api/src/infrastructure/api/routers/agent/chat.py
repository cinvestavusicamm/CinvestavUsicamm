from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from application.use_cases.agent.chat_rag import ChatRAGUseCase
from infrastructure.api.dependencies import get_chat_use_case

# --- ESTA LÍNEA ES LA QUE TE FALTA O ESTÁ MAL ---
router = APIRouter() 

class ChatRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask_agent(
    request: ChatRequest,
    use_case: ChatRAGUseCase = Depends(get_chat_use_case)
):
    try:
        response = await use_case.run(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))