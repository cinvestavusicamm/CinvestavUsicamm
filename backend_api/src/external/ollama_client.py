import os
import logging
import json  # <--- Agregado
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
        """Genera respuesta usando Ollama Generate API (/api/generate)."""
        try:
            logger.info(f"Generando respuesta con modelo: {self.model}")

            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"Responde de forma clara y concisa. {prompt}",
                    "stream": False,
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
                return data.get("response", "")

            logger.error(f"Ollama error: {response.status_code} - {response.text}")
            return "Error: el modelo no pudo generar respuesta."

        except httpx.TimeoutException:
            logger.error("Timeout con Ollama")
            return "El agente tardó demasiado en responder."
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Error interno del agente."

    async def generate_streaming_response(self, prompt: str):
        """Genera respuesta en streaming usando Ollama"""
        try:
            logger.info(f"Generando streaming con modelo: {self.model}")
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"Responde de forma clara y concisa. {prompt}",
                    "stream": True,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 500,
                        "num_ctx": 1024
                    }
                },
                timeout=120.0
            ) as response:
                
                buffer = ""
                async for chunk in response.aiter_bytes():
                    buffer += chunk.decode('utf-8')
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        try:
                            chunk_data = json.loads(line)
                            if "response" in chunk_data:
                                content = chunk_data["response"]
                                if content:
                                    yield content
                            if chunk_data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                                
        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            yield f"Error: {str(e)}"

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Obtiene embedding de Ollama."""
        try:
            logger.info(f"Obteniendo embedding con modelo: {self.embed_model}")

            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.embed_model, "prompt": text},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding", [])
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