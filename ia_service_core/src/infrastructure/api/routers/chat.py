from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.application.use_cases.chat_rag import ChatRAGUseCase
from src.infrastructure.api.dependencies import get_chat_use_case
from src.infrastructure.api.security import verify_internal_key

# Inicialización del Router
router = APIRouter() 

# Modelo de Petición (DTO)
class ChatRequest(BaseModel):
    query: str

    role: str = "teacher" 
   
    user_id: str = "anon"

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
        
        print(f"Error crítico en Microservicio IA (/ask): {e}")
        raise HTTPException(status_code=500, detail=str(e))