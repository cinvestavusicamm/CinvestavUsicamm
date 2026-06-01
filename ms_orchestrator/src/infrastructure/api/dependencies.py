"""Dependency injection for FastAPI application."""

import logging
from typing import AsyncGenerator

from ms_orchestrator.src.infrastructure.config import settings
from ms_orchestrator.src.infrastructure.external.clients import ServiceRegistry

logger = logging.getLogger(__name__)

# Global service registry instance
_service_registry: ServiceRegistry | None = None


async def init_service_registry() -> ServiceRegistry:
    """Initialize the service registry on application startup."""
    global _service_registry

    logger.info("Initializing service registry")

    _service_registry = ServiceRegistry(
        validation_url=settings.VALIDATION_SERVICE_URL,
        backend_url=settings.BACKEND_API_URL,
        db_url=settings.MICROSERVICE_DB_URL,
        django_url=settings.DJANGO_BACKEND_URL,
    )

    # Perform health checks
    health_status = await _service_registry.health_check_all()
    logger.info(
        "Service registry health check completed",
        extra={"status": health_status},
    )

    return _service_registry


async def cleanup_service_registry() -> None:
    """Cleanup service registry on application shutdown."""
    global _service_registry

    if _service_registry is not None:
        logger.info("Cleaning up service registry")
        await _service_registry.close_all()
        _service_registry = None


async def get_service_registry() -> AsyncGenerator[ServiceRegistry, None]:
    """Dependency injection for ServiceRegistry."""
    global _service_registry

    if _service_registry is None:
        raise RuntimeError("Service registry not initialized")

    yield _service_registry
