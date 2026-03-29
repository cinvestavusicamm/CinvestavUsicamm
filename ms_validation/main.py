"""ms_validation.main

This is the Composition Root: it assembles the FastAPI app, registers
middleware, and mounts routes.
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# 1. Importar ambos routers (Validación e Ingesta)
from ms_validation.presentation.routes import router as validation_router
from ms_validation.presentation.rules import router as rules_router

# ──────────────────────────────────────────────
# Logging (Traceability)
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger("ms_validation")

# ──────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────

app = FastAPI(
    title="EscalafonIA — Servicio de Validación y Conocimiento",
    description=(
        "Evalúa procesos docentes contra la normativa vigente "
        "inyectada mediante RAG (Motor de Ingesta y Validación)."
    ),
    version="1.0.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Middleware de Observabilidad (X-Request-ID) ──
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.monotonic()
    
    response = await call_next(request)
    
    process_time = time.monotonic() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    response.headers["X-Request-ID"] = request_id
    
    logger.info(f"RID: {request_id} | Path: {request.url.path} | Time: {process_time:.4f}s")
    return response

# ── Routes Registration ──
# 2. Registrar el router original de validación
app.include_router(validation_router, prefix="/api", tags=["Validación"])

# 3. Registrar el NUEVO router de ingesta de normativas
app.include_router(rules_router, prefix="/api/rules", tags=["Base de Conocimiento"])

# ── Health check ──
@app.get("/health", tags=["Infra"])
async def health():
    return {"service": "ms_validation", "status": "ok"}