"""application.use_cases.generate_report_use_case
Orquestador asíncrono. Flujo Universal impulsado por RAG con guardado efímero
y trazabilidad persistente en PostgreSQL.
"""
import os
import logging
import traceback
from datetime import datetime, timezone

# Importaciones limpias (sin el prefijo 'src.')
from infrastructure.adapters.job_metadata_store import JobMetadataStore
from infrastructure.adapters.postgres_adapter import PostgresAdapter
from infrastructure.adapters.qdrant_adapter import QdrantAdapter
from infrastructure.adapters.ollama_adapter import OllamaAdapter
from application.services.report_builder import ReportBuilder
from infrastructure.adapters.weasyprint_report_generator import WeasyPrintReportGenerator

logger = logging.getLogger("ms_reports.use_case")

class GenerateReportUseCase:
    def __init__(self):
        self.job_store = JobMetadataStore.from_env()
        self.db = PostgresAdapter()  # Inicializamos el adaptador de Postgres
        self.qdrant = QdrantAdapter()
        self.ollama = OllamaAdapter()
        self.builder = ReportBuilder()

    def run(self, payload: dict, job_id: str) -> None:
        # Importamos la tarea aquí para evitar dependencias circulares al inicio
        from infrastructure.workers.tasks import delete_ephemeral_report

        # Reemplazo de utcnow() por la forma moderna y segura de Python 3.12+
        start_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        process_id = payload.get("process_id", "UNKNOWN")
        profile_name = payload.get("profile_name", "USICAMM_PVEB")
        
        # FR3: Extraemos el ID de la institución (si no viene, usa 'default')
        institution_id = payload.get("institution_id", "default")
        
        try:
            self.job_store.update_status(job_id, "STARTED")

            # 1. RAG: Buscar reglas en Qdrant (Manejando la ausencia de documentos)
            logger.info(f"[{job_id}] Buscando reglas de diseño para: {profile_name}")
            try:
                context_rules = self.qdrant.search_style_rules(f"Estructura para {profile_name}")
            except Exception as e:
                logger.warning(f"[{job_id}] Qdrant falló o está vacío. Usando generador dinámico. Error: {e}")
                context_rules = ""
            
            # Si la base vectorial está vacía (no se ha inyectado el PDF), creamos reglas dinámicas
            if not context_rules or context_rules.strip() == "":
                report_type_clean = payload.get("report_type", "Reporte Dinámico").replace("_", " ").title()
                context_rules = f"""
                Eres un diseñador de reportes estructurados. DEBES obedecer este esquema basándote estrictamente en los datos del payload:
                1. Configura el 'header.title' como: "{report_type_clean}".
                2. Configura el 'header.subtitle' como: "{profile_name}".
                3. Analiza los objetos dentro del nodo "payload". 
                4. Por cada grupo de datos descriptivos, genera una sección de tipo 'key_value'.
                5. Si encuentras un diccionario con datos puramente numéricos (ej. métricas, estadísticas), genera obligatoriamente una sección de tipo 'chart' para graficarlos.
                6. NO inventes información. Usa SOLO los datos proporcionados en el payload.
                """

            # 2. LLM: Generar Layout Universal
            logger.info(f"[{job_id}] Generando layout universal con Ollama...")
            layout_schema = self.ollama.generate_universal_layout(context_rules, payload)

            # 3. Ensamblaje HTML y Gráficas (Inyectando el Logo)
            logger.info(f"[{job_id}] Construyendo HTML Universal para institución: {institution_id}...")
            html_content = self.builder.build_universal_html(layout_schema, institution_id=institution_id)
            
            # 4. Generación PDF
            logger.info(f"[{job_id}] Renderizando PDF con WeasyPrint...")
            pdf_bytes = WeasyPrintReportGenerator.generate_pdf(html_content)

            # 5. Guardado Físico Temporal
            reports_dir = "/srv/ms3_reports/static/reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            filename = f"report_{job_id}.pdf"
            local_path = os.path.join(reports_dir, filename)
            
            with open(local_path, "wb") as f:
                f.write(pdf_bytes)
                f.flush()
                os.fsync(f.fileno())

            public_url = f"/static/reports/{filename}"

            # 6. Finalización y Auditoría Persistente
            self.job_store.set_result(job_id, public_url)
            self.job_store.update_status(job_id, "SUCCESS")

            # Título inteligente
            timestamp_amigable = datetime.now().strftime('%Y-%m-%d %H:%M')
            report_title = f"{profile_name} - {timestamp_amigable}"

            try:
                # Usamos self.db en lugar de self.supabase
                self.db.insert_audit_record("escalafonia_reports_audit", {
                    "job_id": job_id, 
                    "process_id": process_id, 
                    "status": "AVAILABLE",  
                    "s3_path": public_url, 
                    "started_at": start_ts, 
                    "finished_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "error_message": report_title  
                })
            except Exception as e:
                logger.warning(f"[{job_id}] No se pudo guardar la auditoría en PostgreSQL: {e}")

            # 7.Programar la autodestrucción
            logger.info(f"[{job_id}] Reporte creado. Programando autodestrucción en 5 minutos...")
            delete_ephemeral_report.apply_async(args=[job_id, local_path], countdown=300)

        except Exception as exc:
            tb = traceback.format_exc()
            logger.error(f"[{job_id}] Fallo crítico: {tb}")
            self.job_store.set_error(job_id, str(exc))
            self.job_store.update_status(job_id, "FAILED")
            
            try:
                self.db.insert_audit_record("escalafonia_reports_audit", {
                    "job_id": job_id, "process_id": process_id, "status": "FAILED", 
                    "error_message": str(exc), "started_at": start_ts, 
                    "finished_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                })
            except Exception:
                pass
            raise