from fastapi import APIRouter, HTTPException
from typing import List

from src.domain.schemas import Course
from src.infrastructure.storage import cursos

router = APIRouter(tags=["Cursos"])

@router.get("/cursos", response_model=List[Course])
async def list_cursos():
    return cursos

@router.post("/cursos", response_model=Course, status_code=201)
async def create_curso(payload: Course):
    payload.id = len(cursos) + 1
    cursos.append(payload)
    return payload

@router.get("/cursos/{curso_id}", response_model=Course)
async def get_curso(curso_id: int):
    curso = next((item for item in cursos if item.id == curso_id), None)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso
