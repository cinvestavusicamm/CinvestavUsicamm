from fastapi import APIRouter, HTTPException
from typing import List

from src.domain.schemas import Employee
from src.infrastructure.storage import empleados

router = APIRouter(tags=["AdministraciÃ³n"])

@router.get("/empleados", response_model=List[Employee])
async def list_empleados():
    return empleados

@router.post("/empleados", response_model=Employee, status_code=201)
async def create_empleado(payload: Employee):
    payload.id = len(empleados) + 1
    empleados.append(payload)
    return payload

@router.put("/empleados/{empleado_id}", response_model=Employee)
async def update_empleado(empleado_id: int, payload: Employee):
    index = next((i for i, item in enumerate(empleados) if item.id == empleado_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    payload.id = empleado_id
    empleados[index] = payload
    return payload

@router.delete("/empleados/{empleado_id}")
async def delete_empleado(empleado_id: int):
    index = next((i for i, item in enumerate(empleados) if item.id == empleado_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    empleados.pop(index)
    return {"status": "success", "message": "Empleado eliminado"}
