# ──────────────────────────────────────────────
# ms_validation — Dockerfile para EscalafonIA
# ──────────────────────────────────────────────

FROM python:3.12-slim AS base

# Configuración de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # PYTHONPATH apunta directamente a src para resolver importaciones sin el prefijo "src."
    PYTHONPATH=/app/ms_validation/src

WORKDIR /app

# Instalar dependencias del sistema necesarias (incluyendo curl para el healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── 1. Instalar ia_common (Capa de infraestructura compartida) ──
COPY ia_common/ /app/ia_common/
RUN pip install --no-cache-dir /app/ia_common/

# ── 2. Instalar dependencias de ms_validation ──
COPY ms_validation/requirements.txt /app/ms_validation/requirements.txt
RUN pip install --no-cache-dir -r /app/ms_validation/requirements.txt

# ── 3. Copiar código fuente de ms_validation ──
# Copiado seguro y específico apuntando a la nueva estructura src/
COPY ms_validation/src/ /app/ms_validation/src/

# Crear usuario de seguridad (MoProSoft: Seguridad de la información)
RUN useradd -m escalafonia && chown -R escalafonia:escalafonia /app
USER escalafonia

WORKDIR /app/ms_validation

# ── 4. Exposición de puerto ──
EXPOSE 8001

# ── 5. Healthcheck (Requisito de Observabilidad) ──
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# ── 6. Lanzamiento ──
# Ejecuta Uvicorn usando la ruta relativa gracias al PYTHONPATH
CMD ["uvicorn", "infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"]