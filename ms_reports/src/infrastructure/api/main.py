"""infrastructure.api.main
Punto de entrada principal para el microservicio de Reportes.
Implementa Arquitectura Hexagonal y CORS para comunicación inter-servicios.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importaciones limpias apuntando directamente a las carpetas correctas
from infrastructure.api.routers import reports, rules, assets
from infrastructure.config.settings import settings

# --- MANEJO DE CICLO DE VIDA ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de Startup (Antes del yield)
    # Place for startup connectors if needed
    yield
    # Lógica de Shutdown (Después del yield)
    # Clean shutdown hooks
    pass

app = FastAPI(
    title="MS-3 Reports Service (Universal)", 
    version="0.2.0",
    lifespan=lifespan
)

# --- CONFIGURACIÓN DE CORS ---
# Permite que el frontend (puerto 3000) u otros microservicios consuman esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINT HEALTH CHECK ---
@app.get("/health", tags=["system"], summary="Verifica el estado del microservicio")
def health_check():
    return {"status": "ok", "service": "ms_reports", "mode": "stateless_universal"}

# --- RUTAS DE REPORTES Y GESTIÓN ---
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(rules.router, prefix="/api/v1/rules", tags=["admin_rules"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets_management"])

if __name__ == "__main__":
    import uvicorn
    # Usamos los valores de settings, pero por defecto a 0.0.0.0 y 8003
    uvicorn.run(app, host=getattr(settings, "HOST", "0.0.0.0"), port=getattr(settings, "PORT", 8003))