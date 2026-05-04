"""ms_validation.infrastructure.adapters.qdrant_vector_repo

Implementación del repositorio de vectores usando Qdrant.
Actualizado para usar 'query_points', el método más estable de la API 1.9.0+.
"""

import logging
import uuid
from typing import List

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ia_common.application.ports.output import VectorRepository

logger = logging.getLogger("ms_validation.qdrant")

class QdrantVectorRepo(VectorRepository):
    """
    Adaptador para Qdrant optimizado para EscalafonIA.
    """

    def __init__(
        self, 
        url: str, 
        collection_name: str = "ms_validation_rules", 
        vector_size: int = 768
    ):
        self._url = url
        self._collection_name = collection_name
        self._vector_size = vector_size
        self._client: AsyncQdrantClient | None = None

    async def _get_client(self) -> AsyncQdrantClient:
        if self._client is None:
            # Quitamos 'http://' si el cliente ya lo maneja o lo necesita limpio
            clean_url = self._url.replace("http://", "")
            self._client = AsyncQdrantClient(host=clean_url.split(":")[0], port=int(clean_url.split(":")[1]))
            await self._ensure_collection()
        return self._client

    async def _ensure_collection(self) -> None:
        try:
            collections = await self._client.get_collections()
            names = [c.name for c in collections.collections]
            if self._collection_name not in names:
                await self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=VectorParams(
                        size=self._vector_size, 
                        distance=Distance.COSINE
                    ),
                )
                logger.info("Colección '%s' creada.", self._collection_name)
        except Exception as e:
            logger.error("Error en Qdrant Ensure: %s", str(e))

    async def save_document(
        self, content: str, vector: List[float], metadata: dict
    ) -> None:
        client = await self._get_client()
        await client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()), 
                    vector=vector, 
                    payload={**metadata, "content": content}
                )
            ],
        )

    async def search_similarity(self, vector: List[float], limit: int = 3) -> List[str]:
        """
        Búsqueda semántica usando query_points (API estable 1.9.0).
        """
        client = await self._get_client()
        try:
            # Usamos query_points que es más robusto en AsyncQdrantClient
            response = await client.query_points(
                collection_name=self._collection_name,
                query=vector,
                limit=limit,
                with_payload=True
            )
            
            return [hit.payload.get("content", "") for hit in response.points if hit.payload]
        except Exception as e:
            # Si falla el nuevo método, intentamos el tradicional como fallback
            try:
                logger.warning("Fallo query_points, intentando search tradicional...")
                hits = await client.search(
                    collection_name=self._collection_name,
                    query_vector=vector,
                    limit=limit
                )
                return [hit.payload.get("content", "") for hit in hits if hit.payload]
            except Exception as e2:
                logger.error("Error crítico en búsqueda Qdrant: %s", str(e2))
                return []