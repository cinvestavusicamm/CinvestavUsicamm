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

    def __init__(self, model: str = "llama3:8b", embed_model: str = "nomic-embed-text"):
        self.base_url = OLLAMA_BASE_URL
        self.model = model
        self.embed_model = embed_model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def generate_response(self, prompt: str) -> str:
        """Genera respuesta de texto usando Ollama LLM (/v1/completions)."""
        try:
            logger.info(f"Generando respuesta con modelo: {self.model}")
            logger.info(f"Prompt: {prompt[:100]}...")

            response = await self.client.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": 512,
                    "temperature": 0.7
                },
                timeout=120.0
            )

            if response.status_code == 200:
                data = response.json()
                # Ollama devuelve la respuesta en "completion" dentro de results
                if "results" in data and len(data["results"]) > 0:
                    return data["results"][0].get("completion", "")
                return ""
            else:
                logger.error(f"Error de Ollama (completions): {response.status_code} - {response.text}")
                return f"Error: Ollama respondió con código {response.status_code}"

        except httpx.ConnectError as e:
            logger.error(f"No se pudo conectar a Ollama en {self.base_url}: {e}")
            return "Error: No se pudo conectar al servicio de IA"
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return f"Error generando respuesta: {str(e)}"

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
