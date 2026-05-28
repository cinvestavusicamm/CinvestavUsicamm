from abc import ABC, abstractmethod
from typing import List, Optional, AsyncGenerator
class VectorRepository(ABC):
    @abstractmethod
    async def save_document(self, content: str, vector: List[float], metadata: dict):
        """Guarda un documento vectorizado."""
        pass

    @abstractmethod
    async def search_similarity(self, vector: List[float], limit: int = 3) -> List[str]:
        """Busca texto similar basado en vectores."""
        pass

# Contrato para la IA (Tu antiguo client.py debe cumplir esto)
class LLMService(ABC):
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Convierte texto a números."""
        pass

    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """Genera texto respuesta."""
        pass

    @abstractmethod
    async def generate_streaming_response(self, prompt: str) -> AsyncGenerator [str, None]:
        """Nuevo metodo para streaming"""
        pass