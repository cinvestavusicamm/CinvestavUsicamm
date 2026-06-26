"""infrastructure.api.routers.reports
Endpoints para la generación asíncrona de reportes PDF Universales.
Adaptado para el flujo Chat-to-Report de EscalafonIA y soporte de logotipos dinámicos.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import uuid
from typing import Dict, Any, Optional

# Importaciones limpias sin 'src.'
from infrastructure.config.settings import settings
from infrastructure.adapters.job_metadata_store import JobMetadataStore
from infrastructure.workers.tasks import generate_report_task

router = APIRouter()

class GenerateReportRequest(BaseModel):
    # Campos obligatorios para el orquestador
    report_type: str = Field(default="generico", description="Clasificación del reporte a generar")
    profile_name: str = Field(default="General", description="Perfil de diseño a buscar en Qdrant (ej. SEP_Oficial)")
    
    # FR3: Clave para la inyección de activos estáticos (Logos)
    institution_id: str = Field(default="default", description="ID de la institución para inyectar su logo dinámicamente")
    
    # Campo base para la información extraída por el Chat RAG
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos y filtros aplicados por el LLM")

    class Config:
        # Permite que el frontend o el Chat envíen parámetros extra no definidos explícitamente
        extra = "allow"

def get_job_store() -> JobMetadataStore:
    return JobMetadataStore.from_env()

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED, summary="Encola la generación de un reporte PDF universal")
def generate_report(request: GenerateReportRequest, job_store: JobMetadataStore = Depends(get_job_store)):
    job_id = str(uuid.uuid4())
    
    job_store.create_job(job_id)
    
    # Encolar tarea en Celery
    generate_report_task.delay(request.model_dump(exclude_unset=True), job_id)
    
    return {
        "status": "accepted",
        "job_id": job_id, 
        "message": "El reporte se está generando en segundo plano. Consulta el estado con este ID."
    }

@router.get("/status/{job_id}", summary="Consulta el estado y descarga del reporte")
def get_status(job_id: str, job_store: JobMetadataStore = Depends(get_job_store)):
    job_data = job_store.get_job(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job no encontrado en Redis.")
        
    status_str = job_data.get("status", "UNKNOWN")
    
    
    result_url = job_data.get("result") or f"/static/reports/report_{job_id}.pdf"
    
    return {
        "job_id": job_id,
        "status": status_str,
        "download_url": result_url if status_str == "SUCCESS" else None
    }