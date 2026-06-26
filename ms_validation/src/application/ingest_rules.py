"""ms_validation.application.ingest_rules

Caso de uso encargado de procesar documentos normativos (PDFs),
fragmentarlos y almacenarlos en Qdrant (Base de datos vectorial)
para el sistema EscalafonIA.
"""

import logging
from typing import List
import io

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from ia_common.application.ports.output import LLMService, VectorRepository

logger = logging.getLogger("ms_validation.ingest")

class IngestRulesUseCase:
    """
    Orquestador para la ingesta de la normativa de EscalafonIA.
    """

    def __init__(
        self,
        vector_repo: VectorRepository,
        llm_service: LLMService,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ):
        self.vector_repo = vector_repo
        self.llm_service = llm_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def execute(self, file_bytes: bytes, filename: str) -> dict:
        """
        1. Extrae texto del PDF.
        2. Divide el texto en fragmentos (chunks).
        3. Vectoriza cada fragmento con nomic-embed-text.
        4. Guarda en Qdrant.
        """
        if PdfReader is None:
            raise RuntimeError("La librería 'pypdf' no está instalada. Ejecuta: pip install pypdf")

        logger.info("Iniciando ingesta del documento normativo: %s", filename)
        
        # 1. Extraer texto
        text = self._extract_text_from_pdf(file_bytes)
        if not text.strip():
            raise ValueError(f"El documento {filename} parece estar vacío o no es texto seleccionable.")

        # 2. Fragmentar texto (Chunking)
        chunks = self._chunk_text(text)
        logger.info("Documento dividido en %d fragmentos.", len(chunks))

        # 3 y 4. Vectorizar y guardar en Qdrant
        saved_count = 0
        for i, chunk in enumerate(chunks):
            # Limpiar saltos de línea excesivos
            clean_chunk = " ".join(chunk.split())
            
            # Obtener embedding del LLMService (nomic-embed-text)
            vector = await self.llm_service.get_embedding(clean_chunk)
            
            if vector:
                metadata = {
                    "source": filename,
                    "chunk_index": i,
                    "type": "normativa_escalafonia"
                }
                await self.vector_repo.save_document(
                    content=clean_chunk, 
                    vector=vector, 
                    metadata=metadata
                )
                saved_count += 1
            else:
                logger.warning("Fallo al generar embedding para el fragmento %d", i)

        logger.info("Ingesta completada: %d/%d fragmentos guardados en Qdrant.", saved_count, len(chunks))
        
        return {
            "filename": filename,
            "total_chunks_processed": len(chunks),
            "chunks_saved_to_qdrant": saved_count,
            "status": "success"
        }

    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extrae el texto crudo de un archivo PDF en memoria."""
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

    def _chunk_text(self, text: str) -> List[str]:
        """Divide el texto en fragmentos solapados para no perder contexto normativo."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks