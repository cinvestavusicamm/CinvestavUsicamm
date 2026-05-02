"""infrastructure.api.routers.rules

Endpoints para la administración de reglas y normativas de EscalafonIA.
Permite subir los PDFs que alimentarán el motor RAG.
"""

import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

# Importaciones limpias y completas
from application.ingest_rules import IngestRulesUseCase
from application.delete_rules import DeleteRulesUseCase
from infrastructure.api.dependencies import get_ingest_use_case, get_delete_rules_use_case

logger = logging.getLogger("ms_validation.api.rules")
router = APIRouter()

@router.post(
    "/upload",
    summary="Carga un documento PDF normativo a la base de conocimiento",
    status_code=status.HTTP_201_CREATED,
)
async def upload_rule_document(
    file: UploadFile = File(...),
    use_case: IngestRulesUseCase = Depends(get_ingest_use_case)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se admiten archivos en formato PDF."
        )

    try:
        file_bytes = await file.read()
        result = await use_case.execute(file_bytes=file_bytes, filename=file.filename)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Error procesando el documento %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar el documento: {str(e)}"
        )

@router.delete(
    "/{filename}",
    summary="Elimina un documento normativo obsoleto",
    status_code=status.HTTP_200_OK,
)
async def delete_rule_document(
    filename: str,
    use_case: DeleteRulesUseCase = Depends(get_delete_rules_use_case)
):
    """
    Destruye todos los vectores asociados a un archivo PDF específico.
    """
    try:
        result = await use_case.execute(filename=filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Error eliminando el documento %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al intentar eliminar el documento."
        )