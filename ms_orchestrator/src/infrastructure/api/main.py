from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from src.infrastructure.config.settings import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Circuit breaker state
circuit_breaker_state: Dict[str, Dict[str, Any]] = {
    "validation_service": {"failures": 0, "last_failure": None, "state": "closed"},
    "backend_api": {"failures": 0, "last_failure": None, "state": "closed"},
    "microservice_db": {"failures": 0, "last_failure": None, "state": "closed"},
    "django_backend": {"failures": 0, "last_failure": None, "state": "closed"},
}


def check_circuit_breaker(service_name: str) -> bool:
    """Check if circuit breaker is open for a service"""
    state = circuit_breaker_state.get(service_name, {"state": "closed"})
    return state["state"] == "closed"


def record_failure(service_name: str):
    """Record a failure for circuit breaker"""
    if service_name not in circuit_breaker_state:
        return
    
    state = circuit_breaker_state[service_name]
    state["failures"] += 1
    state["last_failure"] = None  # Would use datetime in production
    
    if state["failures"] >= settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD:
        state["state"] = "open"
        logger.warning(f"Circuit breaker opened for {service_name}")


def record_success(service_name: str):
    """Record a success for circuit breaker"""
    if service_name not in circuit_breaker_state:
        return
    
    state = circuit_breaker_state[service_name]
    state["failures"] = 0
    state["state"] = "closed"


@retry(
    stop=stop_after_attempt(settings.RETRY_MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_FACTOR, min=settings.RETRY_INITIAL_DELAY)
)
async def call_service(
    service_url: str,
    service_name: str,
    endpoint: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Call a microservice with retry logic and circuit breaker"""
    
    if not check_circuit_breaker(service_name):
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} is temporarily unavailable (circuit breaker open)"
        )
    
    url = f"{service_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=settings.SERVICE_TIMEOUT) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=payload, headers=headers)
            elif method == "PUT":
                response = await client.put(url, json=payload, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported method: {method}")
            
            response.raise_for_status()
            record_success(service_name)
            
            if settings.ENABLE_RESPONSE_LOGGING:
                logger.info(f"Response from {service_name}: {response.status_code}")
            
            return response.json()
            
        except httpx.HTTPError as e:
            record_failure(service_name)
            logger.error(f"Error calling {service_name}: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail=f"Error calling {service_name}: {str(e)}"
            )


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/services/status")
async def services_status():
    """Get status of all microservices"""
    return {
        "circuit_breakers": circuit_breaker_state,
        "services": {
            "validation_service": settings.VALIDATION_SERVICE_URL,
            "backend_api": settings.BACKEND_API_URL,
            "microservice_db": settings.MICROSERVICE_DB_URL,
            "django_backend": settings.DJANGO_BACKEND_URL,
        }
    }


# Proxy endpoints for each service
@app.api_route("/validation/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_validation(request: Request, path: str):
    """Proxy requests to validation service"""
    method = request.method
    payload = await request.json() if method in ["POST", "PUT"] else None
    headers = dict(request.headers)
    
    return await call_service(
        service_url=settings.VALIDATION_SERVICE_URL,
        service_name="validation_service",
        endpoint=f"/{path}",
        method=method,
        payload=payload,
        headers=headers
    )


@app.api_route("/backend/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_backend(request: Request, path: str):
    """Proxy requests to backend API"""
    method = request.method
    payload = await request.json() if method in ["POST", "PUT"] else None
    headers = dict(request.headers)
    
    return await call_service(
        service_url=settings.BACKEND_API_URL,
        service_name="backend_api",
        endpoint=f"/{path}",
        method=method,
        payload=payload,
        headers=headers
    )


@app.api_route("/database/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_database(request: Request, path: str):
    """Proxy requests to database microservice"""
    method = request.method
    payload = await request.json() if method in ["POST", "PUT"] else None
    headers = dict(request.headers)
    
    return await call_service(
        service_url=settings.MICROSERVICE_DB_URL,
        service_name="microservice_db",
        endpoint=f"/{path}",
        method=method,
        payload=payload,
        headers=headers
    )


@app.api_route("/django/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_django(request: Request, path: str):
    """Proxy requests to Django backend"""
    method = request.method
    payload = await request.json() if method in ["POST", "PUT"] else None
    headers = dict(request.headers)
    
    return await call_service(
        service_url=settings.DJANGO_BACKEND_URL,
        service_name="django_backend",
        endpoint=f"/{path}",
        method=method,
        payload=payload,
        headers=headers
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.infrastructure.api.main:app",
        host=settings.ORCHESTRATOR_HOST,
        port=settings.ORCHESTRATOR_PORT,
        reload=True if settings.ENVIRONMENT == "development" else False,
        workers=settings.ORCHESTRATOR_WORKERS if settings.ENVIRONMENT == "production" else 1
    )
