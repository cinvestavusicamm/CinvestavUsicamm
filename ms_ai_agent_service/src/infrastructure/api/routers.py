from fastapi import APIRouter

from src.domain.schemas import ChatRequest, ChatResponse, EvaluateRequest, EvaluateResponse, QuestionRequest, QuestionResponse

router = APIRouter(tags=["IA"])

@router.post("/ai/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    return ChatResponse(reply=f"Tutor virtual: he recibido tu mensaje '{payload.prompt}' y estoy trabajando en una respuesta.")

@router.post("/ai/evaluar", response_model=EvaluateResponse)
async def evaluar(payload: EvaluateRequest):
    return EvaluateResponse(score=85.0, summary="EvaluaciÃ³n automÃ¡tica generada para el texto proporcionado.")

@router.post("/ai/generar-preguntas", response_model=QuestionResponse)
async def generar_preguntas(payload: QuestionRequest):
    return QuestionResponse(
        questions=[
            "Â¿CuÃ¡l es el objetivo principal de este tema?",
            "Enumera 3 conceptos clave relacionados con la materia.",
        ]
    )
