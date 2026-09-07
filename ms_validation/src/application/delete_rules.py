"""application.delete_rules
Caso de uso para eliminar normativas obsoletas del motor RAG.
"""
import logging

logger = logging.getLogger("ms_validation.application")

class DeleteRulesUseCase:
    def __init__(self, vector_repo):
        self.vector_repo = vector_repo

    async def execute(self, filename: str) -> dict:
        try:
            # Ahora usamos 'await' porque el método en el adaptador es asíncrono
            await self.vector_repo.delete_by_filename(filename)
            
            return {
                "status": "success",
                "message": f"Normativa '{filename}' eliminada. El sistema ya no la usará para validar expedientes."
            }
        except Exception as e:
            logger.error("Error en el caso de uso al eliminar %s: %s", filename, str(e))
            raise ValueError("No se pudo eliminar el documento de la base de conocimiento.")