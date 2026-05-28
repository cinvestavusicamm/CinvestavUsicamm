import httpx
import logging
import json
from typing import List, Optional, AsyncGenerator
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
            logger.info(f"Prompt: {prompt[:100]}...")

            response = await self.client.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": 0.5,
                    "max_tokens": 150,
                    "num_ctx": 1024
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

    async def generate_streaming_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming usando Ollama"""
        try:
            logger.info(f"Generando streaming con modelo: {self.model}")
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Responde de forma clara y concisa."},
                        {"role": "user", "content": prompt}
                    ],
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
                        if line.startswith('data: '):
                            data = line[6:].strip()
                            if data == '[DONE]':
                                break
                            
                            try:
                                if data:
                                    chunk_data = json.loads(data)
                                    if "choices" in chunk_data and chunk_data["choices"]:
                                        delta = chunk_data["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            yield f"Error: {str(e)}"  # CORREGIDO: usar yield en lugar de return
            # No necesitas return explícito aquí, el generator termina después del yield