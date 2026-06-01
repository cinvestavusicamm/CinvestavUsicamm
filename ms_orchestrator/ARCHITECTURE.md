"""
ARCHITECTURE DECISION RECORDS (ADR) - MS_ORCHESTRATOR

This document records the key architectural decisions made for the
Orchestrator microservice, including the rationale and trade-offs.
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-001: Hexagonal Architecture (Ports & Adapters)
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use Hexagonal Architecture (Ports & Adapters) pattern to organize code.

RATIONALE:
- Decouples business logic from external dependencies
- Facilitates testing through ports/interfaces
- Makes it easy to swap implementations (e.g., different HTTP clients)
- Aligns with domain-driven design principles
- Industry standard for microservices

LAYERS:
1. Domain: Business logic, models, exceptions (no dependencies)
2. Application: Use cases, orchestration logic
3. Infrastructure: HTTP clients, configuration, utilities, external services
4. Presentation: HTTP routers, request validation

TRADE-OFFS:
- More layers to understand initially
- Slightly more boilerplate code
- Benefits outweigh costs for maintainability at scale
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-002: Circuit Breaker Pattern for Service Resilience
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Implement Circuit Breaker pattern with states: CLOSED, OPEN, HALF_OPEN.

RATIONALE:
- Prevents cascading failures between microservices
- Fails fast when services are unavailable
- Allows graceful degradation
- Reduces unnecessary requests during outages
- Industry-proven pattern for distributed systems

STATES:
- CLOSED: Normal operation, requests pass through
- OPEN: Too many failures, requests fail immediately
- HALF_OPEN: Testing if service recovered, limited requests allowed

CONFIGURATION:
- CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5 (failures before opening)
- CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60 (seconds before attempting recovery)

TRADE-OFFS:
- Adds complexity to request logic
- Must be properly configured per service
- Benefits: prevents system-wide outages, improves resilience
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-003: Retry Logic with Exponential Backoff
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use exponential backoff for retries on transient failures.

RATIONALE:
- Handles temporary network issues gracefully
- Prevents thundering herd problem with exponential backoff
- Configurable retry attempts and backoff factor
- Works well with Circuit Breaker pattern

ALGORITHM:
- Attempt 1: Immediate
- Attempt 2: Wait 1s (initial_delay)
- Attempt 3: Wait 2s (initial_delay × backoff_factor^1)
- After all attempts: RetryExhaustedError

CONFIGURATION:
- RETRY_MAX_ATTEMPTS = 3
- RETRY_INITIAL_DELAY = 1.0
- RETRY_BACKOFF_FACTOR = 2.0

TRADE-OFFS:
- Can mask underlying service issues if not configured properly
- Must be used with circuit breaker to avoid retry storms
- Benefits: improves success rate for transient failures
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-004: Structured Logging (JSON Format)
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use structured JSON logging for all application events.

RATIONALE:
- Enables machine-readable logs for log aggregation systems
- Supports complex queries in centralized logging (e.g., ELK, Datadog)
- Includes full context in each log entry
- Facilitates correlation IDs for distributed tracing

LOG STRUCTURE:
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "module.name",
  "message": "User action description",
  "request_id": "uuid-1234",
  "extra": { "custom": "fields", "duration_ms": 150 }
}

CONFIGURATION:
- LOG_LEVEL: INFO, DEBUG, WARNING, ERROR
- LOG_FORMAT: json (or text for development)

TRADE-OFFS:
- Slightly larger log entries
- Harder to read in raw form (use log viewer tools)
- Benefits: better observability at scale, easier debugging
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-005: Request ID Tracing
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Generate and propagate unique request IDs through the system.

RATIONALE:
- Enables tracing requests across multiple microservices
- Facilitates debugging of distributed transactions
- Required for compliance and audit logging
- Improves observability

IMPLEMENTATION:
- Generate unique ID for each incoming request
- If client provides X-Request-ID header, use that
- Include ID in all logs for this request
- Return ID in response headers and body

PROPAGATION:
- Include in requests to downstream services
- All services log this ID
- Correlates logs across system

TRADE-OFFS:
- Minimal performance impact (ID generation is fast)
- Requires discipline across all services
- Benefits: huge improvement in debuggability
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-006: Dependency Injection for Service Registry
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use manual dependency injection pattern for ServiceRegistry.

RATIONALE:
- Explicit control over object lifecycle
- Easy to mock in tests
- FastAPI Depends() integration
- Avoids magic framework-specific DI containers

APPROACH:
- ServiceRegistry initialized in app startup event
- Injected via Depends() in route handlers
- Cleaned up in app shutdown event
- Single instance shared across all requests

CONFIGURATION:
- Clients created with URLs from environment
- Circuit breakers and retry policies configured
- Health checks performed at startup

TRADE-OFFS:
- More manual than framework DI (e.g., Spring)
- Flexible and explicit
- Easy to debug and test
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-007: Sequential vs Parallel Workflow Execution
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Support both sequential and parallel workflow execution modes.

RATIONALE:
- Sequential: Ordered dependencies, simpler error handling
- Parallel: Better performance when steps are independent
- Flexibility for different use cases

SEQUENTIAL MODE (Default):
- Steps execute one after another
- Output from step N feeds into step N+1
- Error in one step stops entire workflow
- Predictable execution order

PARALLEL MODE:
- All steps execute concurrently
- No data dependencies between steps
- Faster execution, better resource utilization
- Error in one step doesn't stop others

IMPLEMENTATION:
- asyncio.gather() for parallel execution
- Sequential loop for sequential execution
- Configurable via workflow.parallel flag

CONFIGURATION:
- Type: Boolean field in OrchestratedWorkflow
- Default: False (sequential)

TRADE-OFFS:
- Parallel adds complexity to error handling
- Sequential guarantees order and consistency
- Use parallel only when steps are truly independent
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-008: Service Registry Pattern
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use Service Registry pattern to manage microservice clients.

RATIONALE:
- Centralized location for all service clients
- Consistent configuration across clients
- Easy to add new services
- Facilitates health checking of all services

REGISTRY CONTENTS:
- validation: ValidationServiceClient
- backend: BackendAPIClient
- database: MicroserviceDBClient

EACH CLIENT:
- Has own circuit breaker and retry policy
- Manages HTTP connection pool
- Provides service-specific methods
- Handles errors gracefully

HEALTH CHECKS:
- Called at app startup
- Can be called on-demand
- Returns status of all services

TRADE-OFFS:
- Central point of configuration
- Easy to scale by adding clients
- Slightly tight coupling with known service names
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-009: Pydantic Models for Validation
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use Pydantic models for all request/response validation.

RATIONALE:
- Type-safe request handling
- Automatic validation of input data
- Clear API contracts
- Easy integration with FastAPI
- Built-in documentation generation

SCHEMA HIERARCHY:
- Domain layer: Contains core schemas
- Request models: Define expected input
- Response models: Define guaranteed output
- All inherit from Pydantic BaseModel

VALIDATION FEATURES:
- Type checking
- Required/optional fields
- Field constraints (e.g., min/max)
- Custom validators
- JSON schema generation

TRADE-OFFS:
- Requires defining schemas upfront
- Pydantic handles edge cases well
- Benefits: type safety, documentation, validation
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-010: Error Handling Strategy
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Use custom exception hierarchy with HTTP status code mapping.

RATIONALE:
- Semantic error codes for different failure modes
- Client can understand failure reason
- Proper HTTP status codes for each scenario
- Detailed logging without exposing internals

EXCEPTION HIERARCHY:
- OrchestratorException (base)
  - ServiceUnavailableError → 503
  - ServiceTimeoutError → 504
  - CircuitBreakerOpenError → 503
  - WorkflowExecutionError → 500
  - InvalidRequestError → 400
  - ServiceResponseError → 502
  - RetryExhaustedError → 503

HTTP STATUS MAPPING:
- 400: Invalid request (client error)
- 502: Bad gateway (service error)
- 503: Service unavailable (infrastructure)
- 504: Gateway timeout (timeout)
- 500: Generic error (unexpected)

TRADE-OFFS:
- Comprehensive error handling
- Clear semantics for each error type
- Facilitates better error recovery in clients
"""

# ─────────────────────────────────────────────────────────────────────
# ADR-011: CORS Configuration
# ─────────────────────────────────────────────────────────────────────

"""
DECISION:
Configurable CORS with default allow-all for development.

RATIONALE:
- Security: Control which origins can access the service
- Development: Allow-all simplifies testing
- Production: Restrict to known origins

DEFAULT CONFIGURATION (Development):
- CORS_ALLOW_ORIGINS = ["*"]
- CORS_ALLOW_METHODS = ["*"]
- CORS_ALLOW_HEADERS = ["*"]

PRODUCTION CONFIGURATION (Example):
- CORS_ALLOW_ORIGINS = ["https://escalafon.example.com"]
- CORS_ALLOW_METHODS = ["GET", "POST", "PUT"]
- CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]

TRADE-OFFS:
- Default permissive for ease of development
- Must restrict in production
- Benefits: enables web client access securely
"""

# ─────────────────────────────────────────────────────────────────────
# SUMMARY OF KEY DECISIONS
# ─────────────────────────────────────────────────────────────────────

"""
1. Architecture: Hexagonal (Ports & Adapters)
2. Resilience: Circuit Breaker + Retry with Exponential Backoff
3. Observability: Structured JSON Logging + Request IDs
4. Dependency Management: Manual DI with FastAPI Depends()
5. Workflows: Sequential (default) and Parallel execution modes
6. Services: Centralized Service Registry pattern
7. Validation: Pydantic models for type safety
8. Errors: Custom exception hierarchy with HTTP status mapping
9. API Security: Configurable CORS
10. Configuration: Environment variables via Pydantic Settings

These decisions create a robust, maintainable, and scalable
orchestrator that can handle complex distributed workflows
with proper error handling and observability.
"""
