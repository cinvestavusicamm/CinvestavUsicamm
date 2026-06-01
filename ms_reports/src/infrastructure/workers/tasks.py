"""infrastructure.workers.tasks
Definición de las tareas asíncronas ejecutadas por los Celery Workers.
Actualizado para Arquitectura Hexagonal y protocolo de Reportes Efímeros
conectado a la base de datos centralizada (PostgreSQL).
"""
import os
import traceback
import gc
import logging
from celery import Task

# Importaciones limpias sin el prefijo 'src.'
from infrastructure.workers.celery_app import celery_app
from infrastructure.adapters.job_metadata_store import JobMetadataStore
from infrastructure.adapters.postgres_adapter import PostgresAdapter
from application.use_cases.generate_report_use_case import GenerateReportUseCase

logger = logging.getLogger("ms_reports.worker")

class ReportTaskBase(Task):
    """Base Task que actualiza los metadatos del job en caso de fallo crítico."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            job_id = None
            if args and len(args) >= 2:
                job_id = args[1]
            else:
                job_id = kwargs.get("job_id")
            if job_id:
                job_store = JobMetadataStore.from_env()
                job_store.update_status(job_id, "FAILED")
                try:
                    tb = traceback.format_exc()
                except Exception:
                    tb = str(exc)
                sanitized = (tb or str(exc))[-3000:]
                job_store.set_error(job_id, sanitized)
        except Exception:
            pass
        return super().on_failure(exc, task_id, args, kwargs, einfo)

# Nombre de tarea explícito para el registro exacto en el Broker
@celery_app.task(
    name="infrastructure.workers.tasks.generate_report_task",
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
    retry_jitter=True,
    base=ReportTaskBase,
)
def generate_report_task(self, payload: dict, job_id: str):
    """Tarea principal para encolar la generación de PDF."""
    logger.info(f"[{job_id}] Iniciando tarea en background para reporte EscalafonIA.")
    job_store = JobMetadataStore.from_env()
    job_store.update_status(job_id, "STARTED")
    try:
        usecase = GenerateReportUseCase()
        usecase.run(payload, job_id)
        logger.info(f"[{job_id}] Tarea completada con éxito.")
    except Exception as exc:  # noqa: B902
        tb = traceback.format_exc()
        sanitized = tb[-3000:]
        logger.error(f"[{job_id}] Fallo en la tarea: {str(exc)}")
        try:
            job_store.set_error(job_id, sanitized)
        except Exception:
            pass
        try:
            gc.collect()
        except Exception:
            pass
        raise

# --- NUEVA TAREA: AUTODESTRUCCIÓN DE REPORTES EFÍMEROS ---
@celery_app.task(
    name="infrastructure.workers.tasks.delete_ephemeral_report",
    ignore_result=True  # No necesitamos guardar el resultado de esta tarea de limpieza en Redis
)
def delete_ephemeral_report(job_id: str, file_path: str):
    """
    Destruye el archivo PDF físico del servidor y actualiza la base de datos local
    para marcarlo como eliminado, conservando la trazabilidad.
    """
    logger.info(f"[{job_id}] Iniciando protocolo de autodestrucción del reporte...")
    
    # 1. Eliminar el archivo físico para liberar memoria
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[{job_id}] Archivo físico eliminado exitosamente: {file_path}")
        else:
            logger.warning(f"[{job_id}] El archivo {file_path} ya no existe en el disco.")
    except Exception as e:
        logger.error(f"[{job_id}] Error al intentar eliminar el archivo físico: {str(e)}")
        
    # 2. Actualizar el estado en PostgreSQL (La fuente de verdad)
    try:
        db = PostgresAdapter()
        db.update_audit_status("escalafonia_reports_audit", job_id, "DELETED")
        logger.info(f"[{job_id}] Historial en PostgreSQL actualizado a DELETED.")
    except Exception as e:
        logger.error(f"[{job_id}] Error al actualizar el estado en PostgreSQL: {str(e)}")