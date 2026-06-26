"""ms_validation.infrastructure.adapters.ollama_llm

Adaptador para Ollama con Modo JSON nativo activado.
Garantiza que la salida sea un objeto JSON, eliminando comentarios y texto extra.
"""

import logging
from typing import List, Optional
import httpx

from ia_common.application.ports.output import LLMService

logger = logging.getLogger("ms_validation.ollama")

class OllamaLLMAdapter(LLMService):
    def __init__(
        self,
        base_url: str,
        llm_model: str = "phi3:mini",
        embed_model: str = "nomic-embed-text",
        temperature: float = 0.0,
        timeout: int = 180 
    ):
        self.base_url = base_url
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.temperature = temperature
        self.timeout = timeout

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.embed_model, "prompt": text}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("embedding")
            except Exception as e:
                logger.error(f"Error en embeddings: {e}")
                return None

    async def generate_response(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        # Agregamos "format": "json" para activar el modo determinista de Ollama
        payload = {
            "model": self.llm_model,
            "prompt": prompt,
            "stream": False,
            "format": "json", 
            "options": {
                "temperature": self.temperature,
                "num_predict": 1024, # Suficiente para un dictamen
                "num_ctx": 4096,     # Contexto amplio para entender reglas complejas
                "stop": ["\n\n", "###"]
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                logger.error(f"Error en generación: {e}")
                return ""