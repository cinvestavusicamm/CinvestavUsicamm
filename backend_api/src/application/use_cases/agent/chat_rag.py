from application.ports.agent.output import VectorRepository, LLMService
from domain.agent.prompts import PromptTemplates

class ChatRAGUseCase:
    """
    Orquesta: Pregunta -> Vector -> Búsqueda -> Prompt -> Respuesta
    """
    def __init__(self, db: VectorRepository, llm: LLMService):
        self.db = db
        self.llm = llm

    async def run(self, user_query: str) -> str:
        query_vector = await self.llm.get_embedding(user_query)
        
        if not query_vector:
            query_vector = [0.0] * 768  

        context_chunks = await self.db.search_similarity(query_vector, limit=2)
        context_text = "\n---\n".join(context_chunks) if context_chunks else "Sin contexto relevante."

        full_prompt = PromptTemplates.get_rag_prompt(user_query, context_text)

        response = await self.llm.generate_response(full_prompt)
        return response
