import httpx
import logging
from typing import List, Optional
from application.ports.agent.output import LLMService
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

class OllamaAdapter(LLMService):
    """Adaptador para interactuar con Ollama desde FastAPI."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL  
        self.model = settings.LLM_MODEL or "phi3:mini"
        self.embed_model = settings.EMBEDDING_MODEL or "nomic-embed-text"
        self.client = httpx.AsyncClient(timeout=60.0)

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
                embedding = data.get("data", [{}])[0].get("embedding", [])
                logger.info(f"Embedding obtenido. Dimensión: {len(embedding)}")
                return embedding
            else:
                logger.error(f"Error de Ollama (embeddings): {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error obteniendo embedding: {e}")
            return None

    async def generate_response(self, prompt: str) -> str:
        """Genera texto con Ollama usando /v1/completions."""
        try:
            logger.info(f"Generando respuesta con modelo: {self.model}")
            logger.info(f"Prompt: {prompt[:100]}...")  # primeros 100 chars

            response = await self.client.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": 0.5,
                    "max_tokens": 150,
                    "num_ctx":1024
                },
                timeout=120.0
            )

            if response.status_code != 200:
                logger.error(f"Ollama error {response.status_code}: {response.text}")
                return f"Error: Ollama respondió con código {response.status_code}"

            data = response.json()
            return data["choices"][0]["text"]

        except httpx.ConnectError as e:
            logger.error(f"No se pudo conectar a Ollama en {self.base_url}: {e}")
            return "Error: No se pudo conectar al servicio de IA"
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return f"Error generando respuesta: {str(e)}"

