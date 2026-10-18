from src.application.ports.output import LLMService
from src.domain.exceptions import CourseGenerationError
from src.domain.prompts import PromptTemplates


class GenerateCourseUseCase:
    """Pide al modelo la estructura de un curso y devuelve su texto crudo.

    No pasa por el repositorio de vectores: generar un curso no es responder
    sobre un contexto recuperado, es crear. Por eso no depende de la base de
    datos y no usa el pipeline RAG de ChatRAGUseCase.

    Devuelve el texto tal cual lo escribio el modelo (se le pide JSON, pero
    puede venir con ``` alrededor). Validarlo y normalizarlo es cosa de quien
    lo consume: aqui solo se comprueba que hay algo y que, si fallo, se entere
    quien llama en vez de recibir una cadena de error con un 200.
    """

    def __init__(self, llm: LLMService):
        self.llm = llm

    async def run(self, query: str) -> str:
        prompt = PromptTemplates.get_course_generation_prompt(query)
        return await self._generar(prompt)

    async def modify(self, instruccion: str, curso_json: str) -> str:
        """Aplica un cambio sobre un curso ya existente.

        `curso_json` es el JSON del curso tal como lo manda el cliente; el
        modelo devuelve el curso completo actualizado (ver PromptTemplates).
        """
        prompt = PromptTemplates.get_course_modification_prompt(instruccion, curso_json)
        return await self._generar(prompt)

    async def _generar(self, prompt: str) -> str:
        texto = await self.llm.generate_response(prompt, json_mode=True)

        if not texto or not texto.strip():
            raise CourseGenerationError("el modelo devolvio una respuesta vacia")

        return texto
