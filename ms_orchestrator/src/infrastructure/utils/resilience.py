"""Retry and Circuit Breaker utilities for resilient service calls."""

import asyncio
import logging
from typing import Any, Callable, TypeVar, Optional
from datetime import datetime, timedelta
from enum import Enum
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from ms_orchestrator.src.domain.exceptions import (
    RetryExhaustedError,
    CircuitBreakerOpenError,
    ServiceTimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """States of the circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker implementation for microservice calls.

    Implements the circuit breaker pattern to prevent cascading failures:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered, allowing limited requests
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: tuple = (Exception,),
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.success_count = 0

        logger.info(
            f"CircuitBreaker initialized for {service_name}",
            extra={
                "service": service_name,
                "threshold": failure_threshold,
                "timeout": recovery_timeout,
            },
        )

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute a function with circuit breaker protection."""

        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(
                    f"CircuitBreaker for {self.service_name} transitioning to HALF_OPEN"
                )
            else:
                recovery_time = self.recovery_timeout - int(
                    (datetime.utcnow() - self.last_failure_time).total_seconds()
                )
                logger.warning(
                    f"CircuitBreaker for {self.service_name} is OPEN, "
                    f"will retry in {recovery_time}s"
                )
                raise CircuitBreakerOpenError(self.service_name, recovery_time)

        try:
            result = await func(*args, **kwargs)

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(
                    f"CircuitBreaker for {self.service_name} RECOVERED, "
                    "returning to CLOSED"
                )

            return result

        except self.expected_exception as e:
            self._record_failure()

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning(
                    f"CircuitBreaker for {self.service_name} returned to OPEN "
                    f"after failed recovery attempt: {str(e)}"
                )

            raise

    def _record_failure(self) -> None:
        """Record a failure and update circuit breaker state."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        logger.warning(
            f"Failure recorded for {self.service_name}",
            extra={"failure_count": self.failure_count, "threshold": self.failure_threshold},
        )

        if (
            self.state == CircuitBreakerState.CLOSED
            and self.failure_count >= self.failure_threshold
        ):
            self.state = CircuitBreakerState.OPEN
            logger.error(
                f"CircuitBreaker for {self.service_name} opened after "
                f"{self.failure_count} failures"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.last_failure_time is None:
            return False

        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info(f"CircuitBreaker for {self.service_name} manually reset")


class RetryPolicy:
    """
    Retry policy with exponential backoff.

    Implements intelligent retry logic with exponential backoff and jitter
    to handle transient failures gracefully.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    @property
    def decorator(self) -> Callable:
        """Get tenacity retry decorator configured with this policy."""
        return retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=self.initial_delay, max=60  # Max wait is 60 seconds
            ),
            retry=retry_if_exception_type((ServiceTimeoutError, IOError)),
            reraise=True,
        )

    async def execute_with_retry(
        self, func: Callable, *args: Any, **kwargs: Any
    ) -> Any:
        """Execute a function with retry policy."""
        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                logger.debug(
                    f"Attempt {attempt}/{self.max_attempts} for {func.__name__}"
                )
                return await func(*args, **kwargs)

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt} failed for {func.__name__}: {str(e)}"
                )

                if attempt < self.max_attempts:
                    delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
                    await asyncio.sleep(delay)

        raise RetryExhaustedError(
            service_name=getattr(func, "__name__", "unknown"),
            attempts=self.max_attempts,
            last_error=str(last_error),
        )
