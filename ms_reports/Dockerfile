# ──────────────────────────────────────────────
# ms_reports — Dockerfile para Generación de PDFs
# ──────────────────────────────────────────────
FROM python:3.11-slim

# INYECCIÓN CLAVE: Zona horaria predeterminada
ENV TZ="America/Mexico_City"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/srv/ms3_reports/src:/srv/ms3_reports"

WORKDIR /srv/ms3_reports

# Instalar dependencias del sistema requeridas por WeasyPrint + tzdata
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    pkg-config \
    shared-mime-info \
    build-essential \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente (respetando la nueva estructura)
COPY . .

# Hardening: Crear usuario no-root y asegurar permisos de las carpetas dinámicas
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /srv/ms3_reports/static/reports \
    && mkdir -p /srv/ms3_reports/data \
    && chown -R appuser:appuser /srv/ms3_reports

# Cambiar al usuario seguro
USER appuser

EXPOSE 8003

# Comando de inicio por defecto (FastAPI) apuntando a la nueva ruta en src
CMD ["uvicorn", "infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8003"]