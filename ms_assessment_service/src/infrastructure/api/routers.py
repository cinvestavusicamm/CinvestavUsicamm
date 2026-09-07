from fastapi import APIRouter
from typing import List

from src.domain.schemas import Grade, ReportResponse
from src.infrastructure.storage import calificaciones

router = APIRouter(tags=["Evaluaciones"])

@router.get("/calificaciones", response_model=List[Grade])
async def list_calificaciones():
    return calificaciones

@router.post("/calificaciones", response_model=Grade, status_code=201)
async def create_calificacion(payload: Grade):
    payload.id = len(calificaciones) + 1
    calificaciones.append(payload)
    return payload

@router.get("/reportes", response_model=ReportResponse)
async def reportes():
    if not calificaciones:
        return ReportResponse(total=0, average=0.0, summary="Sin calificaciones registradas")
    average = sum(item.nota for item in calificaciones) / len(calificaciones)
    return ReportResponse(total=len(calificaciones), average=average, summary="Reporte acadÃ©mico generado")
