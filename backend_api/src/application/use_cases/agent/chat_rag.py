from application.ports.agent.output import VectorRepository, LLMService
from domain.agent.prompts import PromptTemplates
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class ChatRAGUseCase:
    """
    Orquesta: Pregunta -> Vector -> Búsqueda -> Prompt -> Respuesta
    """
    def __init__(self, db: VectorRepository, llm: LLMService):
        self.db = db
        self.llm = llm

    async def run(self, user_query: str) -> str:
        """Método original - respuesta completa"""
        query_vector = await self.llm.get_embedding(user_query)
        
        if not query_vector:
            query_vector = [0.0] * 768  

        context_chunks = await self.db.search_similarity(query_vector, limit=2)
        context_text = "\n---\n".join(context_chunks) if context_chunks else "Sin contexto relevante."

        full_prompt = PromptTemplates.get_rag_prompt(user_query, context_text)

        response = await self.llm.generate_response(full_prompt)
        return response

    async def run_streaming(self, user_query: str) -> AsyncGenerator[str, None]:
        """Método para streaming"""
        try:
            # 1. Obtener embedding
            query_vector = await self.llm.get_embedding(user_query)
            
            if not query_vector:
                query_vector = [0.0] * 768

            # 2. Buscar contexto
            context_chunks = await self.db.search_similarity(query_vector, limit=2)
            context_text = "\n---\n".join(context_chunks) if context_chunks else "Sin contexto relevante."

            # 3. Construir prompt
            full_prompt = PromptTemplates.get_rag_prompt(user_query, context_text)

            # 4. Streaming de la respuesta
            async for chunk in self.llm.generate_streaming_response(full_prompt):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error en run_streaming: {e}")
            yield f"Error al generar respuesta: {str(e)}"