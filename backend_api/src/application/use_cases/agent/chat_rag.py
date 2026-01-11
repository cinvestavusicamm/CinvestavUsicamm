from application.ports.agent.output import VectorRepository, LLMService
from domain.agent.prompts import PromptTemplates

class ChatRAGUseCase:
    """
    Orquesta el flujo de: Pregunta -> Vector -> Búsqueda -> Prompt -> Respuesta
    """
    def __init__(self, db: VectorRepository, llm: LLMService):
        self.db = db
        self.llm = llm

    async def run(self, user_query: str) -> str:
        # 1. Convertir la pregunta del usuario en vector numérico
        query_vector = await self.llm.get_embedding(user_query)
        
        if not query_vector:
            return "Error: No pude procesar tu pregunta (Fallo en Embedding)."

        # 2. Buscar fragmentos relevantes en la Base de Datos
        context_chunks = await self.db.search_similarity(query_vector, limit=2)
        
        # 3. Unir los fragmentos en un solo texto
        context_text = "\n---\n".join(context_chunks) if context_chunks else "Sin contexto relevante."

        # 4. Construir el Prompt estricto
        full_prompt = PromptTemplates.get_rag_prompt(user_query, context_text)

        # 5. Generar la respuesta final con la IA
        response = await self.llm.generate_response(full_prompt)
        
        return response