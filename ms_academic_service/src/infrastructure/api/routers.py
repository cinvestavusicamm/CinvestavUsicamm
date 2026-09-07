from fastapi import APIRouter
from typing import List

from src.domain.schemas import Student, Teacher, Group
from src.infrastructure.storage import alumnos, profesores, grupos

router = APIRouter(tags=["AcadÃ©mico"])

@router.get("/alumnos", response_model=List[Student])
async def list_alumnos():
    return alumnos

@router.post("/alumnos", response_model=Student, status_code=201)
async def create_alumno(payload: Student):
    payload.id = len(alumnos) + 1
    alumnos.append(payload)
    return payload

@router.get("/profesores", response_model=List[Teacher])
async def list_profesores():
    return profesores

@router.get("/grupos", response_model=List[Group])
async def list_grupos():
    return grupos
