"""Domain exceptions for the Orchestrator."""


class OrchestratorException(Exception):
    """Base exception for orchestrator errors."""

    def __init__(self, message: str, code: str = "ORCHESTRATOR_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ServiceUnavailableError(OrchestratorException):
    """Raised when a dependent service is unavailable."""

    def __init__(self, service_name: str, details: str = ""):
        message = f"Service '{service_name}' is unavailable. {details}"
        super().__init__(message, "SERVICE_UNAVAILABLE")
        self.service_name = service_name


class ServiceTimeoutError(OrchestratorException):
    """Raised when a service request times out."""

    def __init__(self, service_name: str, timeout_seconds: int):
        message = f"Service '{service_name}' request timed out after {timeout_seconds}s"
        super().__init__(message, "SERVICE_TIMEOUT")
        self.service_name = service_name
        self.timeout_seconds = timeout_seconds


class CircuitBreakerOpenError(OrchestratorException):
    """Raised when circuit breaker is open for a service."""

    def __init__(self, service_name: str, recovery_time: int):
        message = (
            f"Circuit breaker for '{service_name}' is open. "
            f"Will attempt recovery in {recovery_time}s"
        )
        super().__init__(message, "CIRCUIT_BREAKER_OPEN")
        self.service_name = service_name
        self.recovery_time = recovery_time


class WorkflowExecutionError(OrchestratorException):
    """Raised when workflow execution fails."""

    def __init__(self, workflow_id: str, step: int, error_details: str):
        message = f"Workflow '{workflow_id}' failed at step {step}: {error_details}"
        super().__init__(message, "WORKFLOW_EXECUTION_ERROR")
        self.workflow_id = workflow_id
        self.step = step
        self.error_details = error_details


class InvalidRequestError(OrchestratorException):
    """Raised when request validation fails."""

    def __init__(self, validation_errors: list):
        message = f"Request validation failed: {'; '.join(validation_errors)}"
        super().__init__(message, "INVALID_REQUEST")
        self.validation_errors = validation_errors


class ServiceResponseError(OrchestratorException):
    """Raised when a service returns an error response."""

    def __init__(self, service_name: str, status_code: int, response_body: str):
        message = f"Service '{service_name}' returned error {status_code}: {response_body}"
        super().__init__(message, "SERVICE_RESPONSE_ERROR")
        self.service_name = service_name
        self.status_code = status_code
        self.response_body = response_body


class RetryExhaustedError(OrchestratorException):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, service_name: str, attempts: int, last_error: str):
        message = (
            f"All {attempts} retry attempts failed for '{service_name}'. "
            f"Last error: {last_error}"
        )
        super().__init__(message, "RETRY_EXHAUSTED")
        self.service_name = service_name
        self.attempts = attempts
        self.last_error = last_error
