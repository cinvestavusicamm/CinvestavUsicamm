from pydantic import BaseModel
from typing import Optional


class Grade(BaseModel):
    id: Optional[int] = None
    alumno_id: int
    materia: str
    nota: float
    comentario: Optional[str] = None


class ReportResponse(BaseModel):
    total: int
    average: float
    summary: str
