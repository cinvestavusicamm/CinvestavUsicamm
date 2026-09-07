import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import JSONResponse

from src.infrastructure.api.routers import router
from src.infrastructure.config import settings
from src.infrastructure.logging import configure_logging, get_logger

configure_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)
logger = get_logger(settings.SERVICE_NAME)

REQUEST_COUNT = Counter("request_count", "Total HTTP requests", ["service", "method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency in seconds", ["service", "endpoint"])

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

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    path = request.url.path
    method = request.method
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as error:
        logger.error(
            "Unhandled exception",
            extra={
                "request_id": request_id,
                "service": settings.SERVICE_NAME,
                "method": method,
                "path": path,
                "error": str(error),
            },
        )
        raise
    duration = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    REQUEST_COUNT.labels(settings.SERVICE_NAME, method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(settings.SERVICE_NAME, path).observe(duration)
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "service": settings.SERVICE_NAME,
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": int(duration * 1000),
        },
    )
    return response

app.include_router(router, prefix=settings.API_PREFIX)

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
        port=8104,
        log_level=settings.LOG_LEVEL.lower(),
        reload=False,
    )
