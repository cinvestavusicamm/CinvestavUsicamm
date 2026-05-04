from fastapi import APIRouter
import requests

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """
Eres un asistente virtual para una plataforma de capacitación docente (USICAMM).

Reglas:
- Habla de forma amable y paciente
- Explica como si el usuario no fuera experto en tecnología
- Usa frases simples, claras
- Genera confianza (ej: "No te preocupes, te ayudo 😊")
- Explica la página actual  si se proporciona contexto
-la información que se te da es la única que tienes, no inventes nada
- Si no sabes la respuesta, di que no lo sabes, no inventes nada
- si el usuario te pregunta algo que no está relacionado con la plataforma, dile que no puedes responder esa pregunta
-La información que das debe ser muy corta y breve para que el usuario no se sienta abrumado, si el usuario necesita más información, él te lo pedirá
-Explica brevemente esta sección en máximo 2 líneas
"""

@router.post("/assistant")
async def assistant(data: dict):
    user_message = data.get("message", "")
    context = data.get("context", "")

    prompt = f"""
{SYSTEM_PROMPT}

Contexto de la página:
{context}

Usuario:
{user_message}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "phi3",  # importante por tu RAM
        "prompt": prompt,
        "stream": False
    })

    return {
        "response": response.json()["response"]
    }