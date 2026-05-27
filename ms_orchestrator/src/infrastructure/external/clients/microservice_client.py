"""HTTP client for communication with external microservices."""

import asyncio
import logging
from typing import Any, Dict, Optional
import httpx

from ms_orchestrator.src.domain.exceptions import (
    ServiceUnavailableError,
    ServiceTimeoutError,
    ServiceResponseError,
)
from ms_orchestrator.src.infrastructure.utils.resilience import (
    CircuitBreaker,
    RetryPolicy,
)
from ms_orchestrator.src.infrastructure.config import settings

logger = logging.getLogger(__name__)


class MicroserviceClient:
    """
    Base client for communicating with microservices.

    Provides resilient HTTP communication with circuit breaker, retry logic,
    and comprehensive error handling.
    """

    def __init__(
        self,
        service_name: str,
        base_url: str,
        timeout: int = 30,
        circuit_breaker_config: Optional[Dict[str, Any]] = None,
    ):
        self.service_name = service_name
        self.base_url = base_url
        self.timeout = timeout

        # Initialize circuit breaker
        cb_config = circuit_breaker_config or {}
        self.circuit_breaker = CircuitBreaker(
            service_name=service_name,
            failure_threshold=cb_config.get(
                "failure_threshold",
                settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            ),
            recovery_timeout=cb_config.get(
                "recovery_timeout",
                settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            ),
        )

        # Initialize retry policy
        self.retry_policy = RetryPolicy(
            max_attempts=settings.RETRY_MAX_ATTEMPTS,
            initial_delay=settings.RETRY_INITIAL_DELAY,
            backoff_factor=settings.RETRY_BACKOFF_FACTOR,
        )

        # HTTP client configuration
        self.http_client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
        )

        logger.info(
            f"MicroserviceClient initialized for {service_name}",
            extra={"service": service_name, "base_url": base_url},
        )

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform a POST request to the microservice."""
        return await self._request("POST", endpoint, json_data, headers, **kwargs)

    async def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform a GET request to the microservice."""
        return await self._request(
            "GET", endpoint, None, headers, params=params, **kwargs
        )

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform a PUT request to the microservice."""
        return await self._request("PUT", endpoint, json_data, headers, **kwargs)

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform a DELETE request to the microservice."""
        return await self._request("DELETE", endpoint, None, headers, **kwargs)

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute HTTP request with resilience patterns."""

        async def _execute():
            try:
                logger.debug(
                    f"Calling {self.service_name} {method} {endpoint}",
                    extra={"method": method, "endpoint": endpoint},
                )

                response = await self.http_client.request(
                    method,
                    endpoint,
                    json=json_data,
                    headers=headers,
                    params=params,
                    **kwargs,
                )

                # Handle HTTP errors
                if response.status_code >= 400:
                    logger.error(
                        f"Service {self.service_name} returned error {response.status_code}",
                        extra={
                            "service": self.service_name,
                            "status_code": response.status_code,
                            "endpoint": endpoint,
                        },
                    )

                    raise ServiceResponseError(
                        service_name=self.service_name,
                        status_code=response.status_code,
                        response_body=response.text[:500],  # Limit to 500 chars
                    )

                return response.json()

            except asyncio.TimeoutError as e:
                logger.error(
                    f"Timeout calling {self.service_name}",
                    extra={"service": self.service_name, "timeout": self.timeout},
                )
                raise ServiceTimeoutError(self.service_name, self.timeout) from e

            except httpx.ConnectError as e:
                logger.error(
                    f"Connection error to {self.service_name}",
                    extra={"service": self.service_name},
                )
                raise ServiceUnavailableError(
                    self.service_name, f"Connection failed: {str(e)}"
                ) from e

        # Execute with circuit breaker and retry logic
        try:
            return await self.circuit_breaker.call(
                self.retry_policy.execute_with_retry, _execute
            )
        except Exception as e:
            logger.error(
                f"Request to {self.service_name} failed: {str(e)}",
                extra={"service": self.service_name, "endpoint": endpoint},
            )
            raise

    async def health_check(self) -> bool:
        """Check if the microservice is healthy."""
        try:
            response = await self.http_client.get("/health", timeout=5)
            is_healthy = response.status_code == 200
            logger.info(
                f"Health check for {self.service_name}: {'OK' if is_healthy else 'FAILED'}",
                extra={
                    "service": self.service_name,
                    "status_code": response.status_code,
                },
            )
            return is_healthy
        except Exception as e:
            logger.warning(
                f"Health check failed for {self.service_name}: {str(e)}",
                extra={"service": self.service_name},
            )
            return False

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self.http_client.aclose()
        logger.info(f"MicroserviceClient closed for {self.service_name}")
