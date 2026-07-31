import time
import uuid

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest

from src.infrastructure.config import settings
from src.infrastructure.logging import configure_logging, get_logger

configure_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)
logger = get_logger("api_gateway")

REQUEST_COUNT = Counter("gateway_requests_total", "Total gateway requests", ["service", "method", "status"])
REQUEST_LATENCY = Histogram("gateway_request_latency_seconds", "Gateway latency", ["service", "method"])
RATE_LIMIT_STATE = {}

app = FastAPI(
    title=settings.SERVICE_TITLE,
    description=settings.SERVICE_DESCRIPTION,
    version=settings.SERVICE_VERSION,
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

SERVICE_MAP = {
    "auth": settings.AUTH_SERVICE_URL,
    "academico": settings.ACADEMIC_SERVICE_URL,
    "evaluaciones": settings.ASSESSMENT_SERVICE_URL,
    "cursos": settings.COURSE_SERVICE_URL,
    "admin": settings.ADMIN_SERVICE_URL,
    "notificaciones": settings.NOTIFICATION_SERVICE_URL,
    "ia": settings.AI_AGENT_SERVICE_URL,
}

RATE_LIMIT = 120
RATE_WINDOW_SECONDS = 60

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.middleware("http")
async def simple_rate_limiter(request: Request, call_next):
    remote = request.client.host if request.client else "unknown"
    now = time.time()
    record = RATE_LIMIT_STATE.setdefault(remote, {"count": 0, "created": now})
    if now - record["created"] > RATE_WINDOW_SECONDS:
        record.update({"count": 0, "created": now})
    record["count"] += 1
    if record["count"] > RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)

@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(service: str, path: str, request: Request):
    target = SERVICE_MAP.get(service)
    if not target:
        return JSONResponse(status_code=404, content={"detail": "Servicio no registrado"})

    url = f"{target}/api/v1/{path}"
    headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
    body = await request.body()
    params = dict(request.query_params)
    method = request.method

    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(method, url, content=body, headers=headers, params=params)
        except Exception:
            if service == "ia":
                return JSONResponse(status_code=503, content={"detail": "Servicio temporalmente no disponible"})
            return JSONResponse(status_code=502, content={"detail": "Error al comunicarse con el servicio upstream"})

    REQUEST_COUNT.labels(service, method, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(service, method).observe(response.elapsed.total_seconds())
    return Response(status_code=response.status_code, content=response.content, headers=dict(response.headers))

@app.get("/health", tags=["Infra"])
async def health():
    return {"service": settings.SERVICE_NAME, "status": "ok"}

@app.get("/metrics", include_in_schema=False)
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.infrastructure.api.main:app",
        host="0.0.0.0",
        port=8100,
        log_level=settings.LOG_LEVEL.lower(),
    )
