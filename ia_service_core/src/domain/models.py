from pydantic import BaseModel
from typing import Optional, List

# Entidad para representar un fragmento de normativa
class Documento(BaseModel):
    contenido: str
    fuente: str
    pagina: Optional[int] = None
    vector: Optional[List[float]] = None

# Entidad para mensajes del chat
class Mensaje(BaseModel):
    rol: str  # "usuario" o "asistente"
    contenido: str