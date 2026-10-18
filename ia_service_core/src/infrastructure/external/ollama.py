import httpx
from typing import List
from src.application.ports.output import LLMService
from src.infrastructure.config.settings import settings

class OllamaAdapter(LLMService):
    """
    Implementación real que habla con el servidor de Ollama.
    """
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.embed_model = settings.EMBEDDING_MODEL

    async def get_embedding(self, text: str) -> List[float]:
        """Consulta a Ollama para obtener el vector numérico del texto."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.embed_model, "prompt": text},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json().get("embedding", [])
            except Exception as e:
                print(f"Error conectando con Ollama (Embedding): {e}")
                return []

    async def generate_response(self, prompt: str, json_mode: bool = False) -> str:
        """Pide a Ollama que complete el texto (Generate).

        Con `json_mode` se anade `format: "json"` para que el modelo devuelva
        solo un objeto JSON valido (lo usan generacion y modificacion de
        cursos). El chat RAG lo deja en False porque quiere texto redactado.

        Si Ollama falla, la excepcion de httpx sube tal cual. Antes se
        capturaba y se devolvia una cadena "Error generando respuesta: ...",
        que el router empaquetaba en un 200: el fallo era indistinguible de una
        respuesta del modelo (ver DEUDA-12 en PLAN.md). El router traduce la
        excepcion a un codigo HTTP.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3} # Menos creativo, más preciso
        }
        if json_mode:
            payload["format"] = "json"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=settings.OLLAMA_GENERATE_TIMEOUT # Darle tiempo para pensar
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")