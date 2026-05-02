import os
from celery import Celery

def create_celery():

    base_redis_url = os.getenv("MS3_REDIS_URL", "redis://redis_reports:6379/0")
    
    broker = os.getenv("MS3_CELERY_BROKER_URL", base_redis_url)
    backend = os.getenv("MS3_CELERY_RESULT_BACKEND", base_redis_url)
    
    celery = Celery("ms3_reports", broker=broker, backend=backend)
    
    # FIX: Aislamiento estricto de colas para no chocar con Django
    celery.conf.task_default_queue = 'reports_queue'
    
    # Optimizaciones para tareas pesadas (PDFs / ML)
    celery.conf.task_acks_late = True
    celery.conf.worker_prefetch_multiplier = 1
    celery.conf.task_soft_time_limit = int(os.getenv("MS3_TASK_SOFT_TIME_LIMIT", "600"))
    
    return celery

celery_app = create_celery()

# Importar tareas para que Celery las registre
try:
    import src.infrastructure.workers.tasks  # noqa: F401
except Exception as e:
    print(f"Error loading MS3 tasks: {e}")