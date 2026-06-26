"""infrastructure.adapters.postgres_adapter

Adaptador oficial para PostgreSQL.
Maneja el registro persistente de reportes (logs de auditoría) para
cumplir con el patrón de "Reportes Efímeros con Trazabilidad Persistente"
utilizando la base de datos centralizada del ecosistema.
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional

from infrastructure.config.settings import settings

logger = logging.getLogger("ms_reports.postgres")

class PostgresAdapter:
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        if not self.db_url:
            logger.warning("DATABASE_URL no configurada. El historial no se guardará.")
        else:
            # Garantizamos que la tabla exista apenas se instancie el adaptador
            self._ensure_table_exists()

    def _get_connection(self):
        """Obtiene una conexión fresca a la base de datos central."""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            logger.error(f"Error crítico al conectar a PostgreSQL: {e}")
            return None

    def _ensure_table_exists(self):
        """Crea la tabla de auditoría en PostgreSQL si no existe."""
        conn = self._get_connection()
        if not conn:
            return

        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS escalafonia_reports_audit (
                            id SERIAL PRIMARY KEY,
                            job_id VARCHAR(255) UNIQUE NOT NULL,
                            process_id VARCHAR(255),
                            status VARCHAR(50),
                            s3_path TEXT,
                            error_message TEXT,
                            started_at TIMESTAMP WITH TIME ZONE,
                            finished_at TIMESTAMP WITH TIME ZONE
                        );
                    """)
                    logger.info("Verificación de tabla de auditoría en PostgreSQL completada.")
        except Exception as e:
            logger.error(f"Error al verificar/crear tabla en PostgreSQL: {e}")
        finally:
            if conn:
                conn.close()

    def insert_audit_record(self, table: str, payload: Dict[str, Any]) -> Optional[dict]:
        """
        Inserta el registro de auditoría del reporte generado.
        Equivalente al insert de Supabase, pero en SQL nativo.
        """
        conn = self._get_connection()
        if not conn:
            return None

        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Construcción dinámica de la consulta SQL
                    columns = ', '.join(payload.keys())
                    # Usamos %s que es el estándar de psycopg2 para prevenir SQL Injection
                    placeholders = ', '.join(['%s'] * len(payload))
                    values = tuple(payload.values())
                    
                    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"
                    
                    cursor.execute(query, values)
                    result = cursor.fetchone()
                    
                    logger.info(f"Auditoría guardada exitosamente en PostgreSQL ({table}).")
                    return dict(result) if result else payload
        except Exception as e:
            logger.error(f"Fallo al insertar auditoría en PostgreSQL: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update_audit_status(self, table: str, job_id: str, new_status: str) -> Optional[dict]:
        """
        Actualiza el estado de un reporte.
        Fundamental para marcar el archivo como 'DELETED' una vez que Celery lo destruye.
        """
        conn = self._get_connection()
        if not conn:
            return None

        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = f"UPDATE {table} SET status = %s WHERE job_id = %s RETURNING *"
                    cursor.execute(query, (new_status, job_id))
                    result = cursor.fetchone()
                    
                    logger.info(f"Estado del reporte {job_id} actualizado a '{new_status}' en PostgreSQL.")
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Fallo al actualizar auditoría en PostgreSQL: {e}")
            return None
        finally:
            if conn:
                conn.close()