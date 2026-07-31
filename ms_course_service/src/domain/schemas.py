from pydantic import BaseModel
from typing import List, Optional


class Resource(BaseModel):
    id: Optional[int] = None
    tipo: str
    titulo: str
    enlace: str


class Module(BaseModel):
    id: Optional[int] = None
    titulo: str
    descripcion: str
    recursos: List[Resource] = []


class Course(BaseModel):
    id: Optional[int] = None
    nombre: str
    descripcion: str
    modulos: List[Module] = []
