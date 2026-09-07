"""Health and status router."""

import logging
from fastapi import APIRouter, Depends
from datetime import datetime

from ms_orchestrator.src.domain import OrchestratorHealthResponse
from ms_orchestrator.src.infrastructure.external.clients import ServiceRegistry
from ms_orchestrator.src.infrastructure.api.dependencies import get_service_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Health"])


@router.get(
    "/health",
    response_model=OrchestratorHealthResponse,
    status_code=200,
    summary="Health check",
    description="Check orchestrator and dependent services health status",
)
async def health_check(
    service_registry: ServiceRegistry = Depends(get_service_registry),
) -> OrchestratorHealthResponse:
    """
    Health check endpoint for the orchestrator.

    Returns the status of the orchestrator and all dependent microservices.

    **Response Fields:**
    - `status`: Overall orchestrator status ("healthy", "degraded", "unhealthy")
    - `version`: Service version
    - `services`: Individual status of each microservice
    """
    logger.info("Health check requested")

    # Check all services
    services_health = await service_registry.health_check_all()

    # Determine overall status
    healthy_count = sum(1 for v in services_health.values() if v)
    total_count = len(services_health)

    if healthy_count == total_count:
        overall_status = "healthy"
    elif healthy_count > 0:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return OrchestratorHealthResponse(
        status=overall_status,
        version="1.0.0",
        services={
            "validation": {"healthy": services_health.get("validation", False)},
            "backend_api": {"healthy": services_health.get("backend", False)},
            "microservice_db": {"healthy": services_health.get("database", False)},
        },
    )


@router.get(
    "/status",
    summary="Orchestrator status",
    description="Get detailed orchestrator status",
)
async def get_status() -> dict:
    """
    Get detailed orchestrator status.

    Returns information about the orchestrator instance, including:
    - Service version
    - Environment
    - Uptime
    - Configuration info
    """
    logger.info("Status requested")

    from ms_orchestrator.src.infrastructure.config import settings

    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "validation_service": settings.VALIDATION_SERVICE_URL,
            "backend_api": settings.BACKEND_API_URL,
            "microservice_db": settings.MICROSERVICE_DB_URL,
        },
    }
