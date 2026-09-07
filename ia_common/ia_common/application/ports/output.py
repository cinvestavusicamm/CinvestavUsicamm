from abc import ABC, abstractmethod
from typing import List


class VectorRepository(ABC):
    @abstractmethod
    async def save_document(self, content: str, vector: List[float], metadata: dict) -> None:
        """Guarda un documento vectorizado."""

    @abstractmethod
    async def search_similarity(self, vector: List[float], limit: int = 3) -> List[str]:
        """Busca texto similar basado en vectores."""


class LLMService(ABC):
    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Convierte texto a números."""

    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """Genera texto respuesta."""
