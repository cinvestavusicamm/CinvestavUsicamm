from pydantic import BaseModel
from typing import Optional


class Student(BaseModel):
    id: Optional[int] = None
    nombre: str
    grado: str
    grupo: str


class Teacher(BaseModel):
    id: Optional[int] = None
    nombre: str
    materia: str
    turno: str


class Group(BaseModel):
    id: Optional[int] = None
    nombre: str
    grado: str
    salon: str
