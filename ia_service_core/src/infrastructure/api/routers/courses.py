from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.use_cases.generate_course import GenerateCourseUseCase
from src.infrastructure.api.dependencies import get_generate_course_use_case
from src.infrastructure.api.routers.chat import error_ia
from src.infrastructure.api.security import verify_internal_key

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateCourseRequest(BaseModel):
    query: str


@router.post("/generate-course", dependencies=[Depends(verify_internal_key)])
async def generate_course(
    request: GenerateCourseRequest,
    use_case: GenerateCourseUseCase = Depends(get_generate_course_use_case)
):
    """Devuelve el JSON de un curso generado por la IA.

    Se entrega como texto en `course_json` (la IA puede envolverlo en ```), para
    que quien lo consume lo extraiga y valide. El servicio no lo guarda ni lo
    valida contra el esquema del curso: eso es de Django, que es quien tiene el
    modelo.
    """
    peticion = request.query.strip()
    if not peticion:
        raise HTTPException(status_code=400, detail="La peticion no puede estar vacia")

    try:
        texto = await use_case.run(peticion)
    except Exception as e:
        logger.exception("Error en /generate-course")
        raise error_ia(e)

    return {
        "course_json": texto,
        "meta": {"processed_by": "ia_service_core"},
    }
