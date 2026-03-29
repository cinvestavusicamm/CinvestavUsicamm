# ──────────────────────────────────────────────
# ms_validation — Dockerfile para EscalafonIA
# Build context: raíz del monorepo (.)
# ──────────────────────────────────────────────

FROM python:3.11-slim AS base

# Configuración de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── 1. Instalar ia_common (Capa de infraestructura compartida) ──
COPY ia_common/ /app/ia_common/
RUN pip install --no-cache-dir /app/ia_common/

# ── 2. Instalar dependencias de ms_validation ──
COPY ms_validation/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ── 3. Copiar código fuente de ms_validation ──
# Copiamos la carpeta completa para que funcione como paquete
COPY ms_validation/ /app/ms_validation/

# Crear usuario de seguridad (MoProSoft: Seguridad de la información)
RUN useradd -m escalafonia && chown -R escalafonia:escalafonia /app
USER escalafonia

# ── 4. Exposición de puerto ──
EXPOSE 8001

# ── 5. Healthcheck (Requisito de Observabilidad) ──
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# ── 6. Lanzamiento ──
CMD ["uvicorn", "ms_validation.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"]