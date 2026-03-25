from application.ports.agent.output import VectorRepository, LLMService
from domain.agent.prompts import PromptTemplates
from typing import AsyncGenerator
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class ChatRAGUseCase:
    def __init__(self, db: VectorRepository, llm: LLMService):
        self.db = db
        self.llm = llm

    async def run(self, user_query: str) -> str:
        try:
            user_query = user_query.strip()
            prompt = PromptTemplates.get_system_prompt() + f"\n\nUsuario: {user_query}\n\nJaqui:"
            response = await self.llm.generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error en run: {e}")
            return "Lo siento, tuve un problema técnico."

    async def run_streaming(self, user_query: str) -> AsyncGenerator[str, None]:
        try:
            user_query = user_query.strip()
            query_lower = user_query.lower()
            
            if any(saludo in query_lower for saludo in ['hola', 'buenos', 'que tal', 'hey']):
                respuestas = [
                    "¡Hola! ¿En qué puedo ayudarte con temas docentes hoy?",
                    "¡Hola! ¿Qué necesitas saber sobre USICAMM, derechos docentes o escalafón?"
                ]
                respuesta = random.choice(respuestas)
                for char in respuesta:
                    yield char
                    await asyncio.sleep(0.01)
                return
            
            prompt = PromptTemplates.get_system_prompt() + f"\n\nUsuario: {user_query}\n\nJaqui:"
            
            async for chunk in self.llm.generate_streaming_response(prompt):
                yield chunk
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            error_msg = "Lo siento, ocurrió un error."
            for char in error_msg:
                yield char
                await asyncio.sleep(0.01)