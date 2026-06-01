"""infrastructure.vector.qdrant_adapter
Adaptador Qdrant para la recuperación de Reglas de Diseño.
Opera mediante búsqueda de similitud semántica.
"""

import logging
from qdrant_client import QdrantClient

from infrastructure.config.settings import settings
from infrastructure.adapters.ollama_adapter import OllamaAdapter

logger = logging.getLogger("ms_reports.qdrant")

class QdrantAdapter:
    def __init__(self):
        clean_url = settings.QDRANT_URL.replace("http://", "")
        host = clean_url.split(":")[0]
        port = int(clean_url.split(":")[1]) if ":" in clean_url else 6333
        
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = settings.QDRANT_COLLECTION
        self.llm_adapter = OllamaAdapter()

    def search_style_rules(self, query: str, limit: int = 3) -> str:
        """
        Busca fragmentos del Manual de Identidad en la base vectorial 
        usando embeddings generados al vuelo.
        """
        # ESTANDARIZACIÓN: Normalizar la búsqueda
        normalized_query = query.lower().strip()

        try:
            vector = self.llm_adapter.get_embedding(normalized_query)
            if not vector:
                logger.warning("Fallo en la generación de embedding. Usando fallback por defecto.")
                return "Aplica colores institucionales neutros (Gris y Blanco). No incluyas logos ni marcas de agua."

            hits = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit
            )
            
            context_chunks = [hit.payload.get("content", "") for hit in hits.points if hit.payload]
            
            if not context_chunks:
                logger.info(f"No se encontraron reglas específicas en Qdrant para: {normalized_query}")
                return "Aplica colores institucionales estándar (Guinda #9D2449 y Dorado #BC955C). No hay logos específicos."
                
            logger.info(f"Se recuperaron {len(context_chunks)} fragmentos de reglas para el perfil.")
            return "\n---\n".join(context_chunks)
            
        except Exception as e:
            logger.error("Error conectando a Qdrant para extraer estilos: %s", str(e))
            return "Modo contingencia. Usa diseño neutral sin recursos externos."
        
    def upsert_rule(self, profile_name: str, text_content: str) -> str:
        """Vectoriza el texto del PDF y lo guarda en Qdrant asociado al perfil."""
        import uuid
        from qdrant_client.models import PointStruct, VectorParams, Distance
        
        vector = self.llm_adapter.get_embedding(text_content)
        if not vector:
            raise ValueError("Ollama no pudo generar el embedding del PDF.")
            
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE)
            )
            
        point_id = str(uuid.uuid4())
        
        # ESTANDARIZACIÓN: Normalizar el perfil al guardar
        normalized_profile = profile_name.lower().strip()
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id, 
                    vector=vector, 
                    payload={"content": text_content, "profile_name": normalized_profile}
                )
            ]
        )
        return point_id

    def delete_rule(self, profile_name: str):
        """Elimina de Qdrant todas las reglas asociadas a un perfil específico."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # ESTANDARIZACIÓN: Normalizar el perfil al eliminar
        normalized_profile = profile_name.lower().strip()
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="profile_name", 
                        match=MatchValue(value=normalized_profile)
                    )
                ]
            )
        )