"""ms_validation.application.validate_process

Caso de uso central: Evalúa trámites de EscalafonIA contra normativa inyectada.
Orquesta el flujo RAG (Retrieval-Augmented Generation) de forma independiente.
"""

import json
import logging
import re
import time
from typing import List
from pydantic import ValidationError

# Imports de puertos (ia_common)
from ia_common.application.ports.output import LLMService, VectorRepository

# Imports internos (ms_validation)
from ms_validation.src.domain.exceptions import LLMOutputParseError
from ms_validation.src.domain.prompts import build_validation_prompt
from ms_validation.src.domain.schemas import (
    ProcessInput,
    ValidationResponse,
    ValidationResult,
)

logger = logging.getLogger("ms_validation.use_case")

class ValidateProcessUseCase:
    """
    Orquestador del flujo RAG para la validación de trámites docentes.
    Mantiene independencia total de otros microservicios.
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
        llm_service: LLMService,
        *,
        rag_top_k: int = 5,
    ):
        self.vector_repo = vector_repo
        self.llm_service = llm_service
        self.rag_top_k = rag_top_k

    async def execute(self, process: ProcessInput) -> ValidationResponse:
        """
        Ejecuta el pipeline completo de validación normativa.
        """
        logger.info(f"Procesando validación para el trámite: {process.process_id}")

        # 1. Generar Vector de consulta (Embedding)
        embed_payload = f"Trámite: {process.process_name}. Categoría: {process.category}. {process.description}"
        query_vector = await self.llm_service.get_embedding(embed_payload)

        if not query_vector:
            logger.error("Error crítico: No se obtuvo el embedding de Ollama.")
            raise LLMOutputParseError(raw_output="", reason="Servicio de embedding fallido.")

        # 2. Recuperar contexto de Qdrant (RAG)
        start_rag = time.monotonic()
        context_chunks = await self.vector_repo.search_similarity(
            query_vector, limit=self.rag_top_k
        )
        rag_latency = (time.monotonic() - start_rag) * 1000
        logger.info(f"RAG finalizado en {rag_latency:.2f}ms. Chunks recuperados: {len(context_chunks)}")

        rag_context = "\n---\n".join(context_chunks) if context_chunks else \
                      "No se encontró normativa específica. Aplicar criterios generales de MoProSoft."

        # 3. Construir prompt y llamar al LLM (Phi-3)
        full_prompt = build_validation_prompt(process, rag_context)
        
        start_llm = time.monotonic()
        raw_response = await self.llm_service.generate_response(full_prompt)
        llm_latency = (time.monotonic() - start_llm) * 1000
        logger.info(f"Inferencia LLM finalizada en {llm_latency:.2f}ms")

        # 4. Parseo robusto del resultado JSON
        result = self._parse_llm_output(raw_response)

        return ValidationResponse(
            process_id=process.process_id,
            result=result,
            sources_used=len(context_chunks),
        )

    @staticmethod
    def _parse_llm_output(raw: str) -> ValidationResult:
        """
        Extrae y valida el JSON devuelto por el LLM con limpieza profunda.
        Diseñado para capturar el objeto JSON incluso si hay texto explicativo.
        """
        if not raw:
            raise LLMOutputParseError(raw_output="", reason="La respuesta del LLM está vacía.")

        # 1. Limpieza de ruido común y bloques Markdown
        cleaned = raw.strip()
        # Elimina indicadores de bloque json o bloques de código
        cleaned = re.sub(r"```json\s*|```\s*", "", cleaned, flags=re.IGNORECASE)

        # 2. Intento de extracción por Ancla (Regex de llaves)
        # Busca el primer '{' y el último '}' para ignorar explicaciones extras
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if not match:
            logger.error(f"No se detectó estructura JSON en la salida: {raw[:100]}...")
            raise LLMOutputParseError(
                raw_output=raw, 
                reason="La IA no generó un bloque de datos { ... } válido."
            )

        json_candidate = match.group(1)

        # 3. Parseo y Validación con Pydantic
        try:
            # Primero validamos que sea un JSON válido estructuralmente
            data = json.loads(json_candidate)
            # Luego validamos contra el esquema de dominio
            return ValidationResult.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Fallo en validación de esquema: {str(e)}")
            raise LLMOutputParseError(
                raw_output=raw,
                reason=f"El dictamen generado no cumple con el formato requerido: {str(e)}"
            )