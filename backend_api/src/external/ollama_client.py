import os
import logging
from typing import List, Optional
import httpx

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "motor_ollama")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"


class OllamaAdapter:
    """Adaptador para interactuar con Ollama LLM y embeddings."""

    def __init__(self, model: str = "phi3:mini", embed_model: str = "nomic-embed-text"):
        self.base_url = OLLAMA_BASE_URL
        self.model = model
        self.embed_model = embed_model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate_response(self, prompt: str) -> str:
        """Genera respuesta usando Ollama Chat API (/v1/chat/completions)."""
        try:
            logger.info(f"Generando respuesta con modelo: {self.model}")

            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Responde de forma clara y concisa."},
                        {"role": "user", "content": prompt}
                    ],
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 120,
                        "num_ctx": 1024
                    }
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )

            logger.error(f"Ollama error: {response.status_code} - {response.text}")
            return "Error: el modelo no pudo generar respuesta."

        except httpx.TimeoutException:
            logger.error("Timeout con Ollama")
            return "El agente tardó demasiado en responder."
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Error interno del agente."


    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Obtiene embedding de Ollama."""
        try:
            logger.info(f"Obteniendo embedding con modelo: {self.embed_model}")

            response = await self.client.post(
                f"{self.base_url}/v1/embeddings",
                json={"model": self.embed_model, "input": text},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                embedding = data.get("data", [])[0].get("embedding", []) if data.get("data") else []
                logger.info(f"Embedding obtenido. Dimensión: {len(embedding)}")
                return embedding
            else:
                logger.error(f"Error de Ollama (embeddings): {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error obteniendo embedding: {e}")
            return None


async def generar_respuesta(prompt: str):
    adapter = OllamaAdapter()
    return await adapter.generate_response(prompt)
