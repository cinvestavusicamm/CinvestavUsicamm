from pydantic import BaseModel
from typing import Optional, List


class Employee(BaseModel):
    id: Optional[int] = None
    nombre: str
    correo: str
    cargo: str
    roles: List[str] = []
