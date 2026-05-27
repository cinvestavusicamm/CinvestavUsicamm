# 🎼 Microservicio Orquestador de Peticiones (ms_orchestrator)

**Versión:** 1.0.0  
**Estado:** Production-Ready  
**Lenguaje:** Python 3.11+  
**Framework:** FastAPI

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [API Endpoints](#api-endpoints)
- [Uso](#uso)
- [Ejemplos](#ejemplos)
- [Patrón de Resiliencia](#patrón-de-resiliencia)
- [Troubleshooting](#troubleshooting)
- [Referencias](#referencias)

---

## 📝 Descripción

El **Microservicio Orquestador de Peticiones** es el componente central que coordina y orquesta todas las peticiones entre los diferentes microservicios del sistema EscalafonIA.

### Propósito

- **Centralización de Lógica de Orquestación:** Proporciona un punto único para coordinar llamadas entre servicios
- **Resiliencia Distribuida:** Implementa patrones de resiliencia (Circuit Breaker, Retry Logic) para garantizar estabilidad
- **Enrutamiento Inteligente:** Dirige peticiones al microservicio apropiado basado en el tipo de operación
- **Trazabilidad:** Mantiene trazas completas de todas las operaciones distribuidas
- **Workflows Complejos:** Permite orquestar workflows multi-paso que abarcan múltiples servicios

---

## ✨ Características

### 🔄 Patrones de Resiliencia

- **Circuit Breaker:** Evita cascadas de fallos con cambios de estado (CLOSED → OPEN → HALF_OPEN)
- **Retry Logic:** Reintentos con backoff exponencial para fallos transitorios
- **Timeouts:** Límites de tiempo para prevenir bloqueos indefinidos
- **Health Checks:** Verificación periódica del estado de servicios dependientes

### 🎯 Orquestación

- **Workflows Secuenciales:** Ejecución paso-a-paso de operaciones
- **Workflows Paralelos:** Ejecución concurrente de pasos independientes
- **Plantillas Predefinidas:** Workflows reutilizables para casos comunes
- **Manejo de Errores:** Captura y propagación inteligente de errores

### 📊 Observabilidad

- **Logging Estructurado:** JSON structured logging con trazabilidad completa
- **Request Tracing:** ID de solicitud único para rastrear a través de sistemas
- **Health Endpoints:** Verificación de estado del orquestador y servicios
- **Métricas:** Duración de operaciones, conteos de intentos, etc.

### 🔐 Seguridad

- **CORS Configurable:** Control de acceso entre orígenes
- **API Key Validation:** Validación opcional de claves API
- **Error Sanitization:** Respuestas de error sin exponer detalles internos

---

## 🏗️ Arquitectura

### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI HTTP Interface                   │
├─────────────────────────────────────────────────────────────┤
│                  Presentation Layer (Routers)               │
├─────────────────────────────────────────────────────────────┤
│              Application Layer (Use Cases)                  │
│  - ValidationOrchestrationUseCase                           │
│  - AnalysisOrchestrationUseCase                             │
│  - WorkflowOrchestrationUseCase                             │
├─────────────────────────────────────────────────────────────┤
│                    Domain Layer (Models)                    │
│  - Schemas, Exceptions, Business Rules                      │
├─────────────────────────────────────────────────────────────┤
│              Infrastructure Layer (External)                │
│  - Circuit Breaker, Retry Policy                            │
│  - Microservice Clients, HTTP Communication                 │
│  - Configuration, Logging                                   │
├─────────────────────────────────────────────────────────────┤
│           External Microservices (HTTP REST)                │
│  - ms_validation (8001)                                     │
│  - ia_service_core (8003)                                   │
│  - microservice_db (8002)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Solicitud

```
Cliente HTTP Request
        ↓
    FastAPI Router
        ↓
  Middleware (Logging, Request ID)
        ↓
  Presentation Layer (Validation)
        ↓
  Application Layer (Use Case)
        ↓
  Service Registry (Client Lookup)
        ↓
  Microservice Clients (Circuit Breaker + Retry)
        ↓
  External Microservices
        ↓
  Response Assembly & Return
```

---

## 📁 Estructura del Proyecto

```
ms_orchestrator/
├── src/
│   ├── __init__.py
│   ├── domain/                    # Domain Layer (Business Logic)
│   │   ├── __init__.py
│   │   ├── schemas.py            # Pydantic models for requests/responses
│   │   └── exceptions.py         # Custom exceptions
│   │
│   ├── application/              # Application Layer (Use Cases)
│   │   ├── __init__.py
│   │   └── orchestration_use_cases.py  # Orchestration logic
│   │
│   ├── infrastructure/           # Infrastructure Layer (External Services)
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py          # FastAPI app composition
│   │   │   ├── dependencies.py  # Dependency injection
│   │   │   └── routers/
│   │   │       ├── __init__.py
│   │   │       ├── validation_router.py
│   │   │       ├── workflow_router.py
│   │   │       └── health_router.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py      # Configuration management
│   │   ├── external/
│   │   │   ├── __init__.py
│   │   │   └── clients/
│   │   │       ├── __init__.py
│   │   │       ├── microservice_client.py  # Base HTTP client
│   │   │       └── service_clients.py      # Service-specific clients
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── resilience.py    # Circuit Breaker & Retry
│   │       └── logger.py        # Structured logging
│   │
│   └── presentation/            # Presentation Layer
│       └── __init__.py
│
├── requirements.txt             # Python dependencies
├── Dockerfile                  # Container image definition
├── docker-compose.yml          # Service orchestration (dev)
├── .env.example               # Environment variables example
└── README.md                  # This file
```

---

## 🚀 Instalación

### Prerequisitos

- Python 3.11+
- Docker & Docker Compose
- pip o uv

### Local Development

```bash
# 1. Clone the repository
git clone <repository-url>
cd CinvestavUsicamm

# 2. Navigate to orchestrator directory
cd ms_orchestrator

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy and configure environment
cp .env.example .env
# Edit .env with your configuration

# 6. Run the service
uvicorn src.infrastructure.api.main:app --reload --port 8000
```

### Docker Deployment

```bash
# Build image
docker build -t escalafon_orchestrator:latest .

# Run container (standalone)
docker run -p 8000:8000 \
  -e VALIDATION_SERVICE_URL=http://localhost:8001 \
  -e BACKEND_API_URL=http://localhost:8003 \
  -e MICROSERVICE_DB_URL=http://localhost:8002 \
  escalafon_orchestrator:latest

# Or use docker-compose
docker-compose up -d
```

---

## ⚙️ Configuración

### Environment Variables

```bash
# Service Identity
SERVICE_NAME=ms_orchestrator
SERVICE_VERSION=1.0.0
ENVIRONMENT=development

# Server Configuration
ORCHESTRATOR_HOST=0.0.0.0
ORCHESTRATOR_PORT=8000

# Microservices URLs
VALIDATION_SERVICE_URL=http://localhost:8001
BACKEND_API_URL=http://localhost:8003
MICROSERVICE_DB_URL=http://localhost:8002

# Communication Settings
SERVICE_TIMEOUT=30
SERVICE_CONNECT_TIMEOUT=10

# Resilience Configuration
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_FACTOR=2.0
RETRY_INITIAL_DELAY=1.0

CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # json or text
ENABLE_REQUEST_LOGGING=true
ENABLE_RESPONSE_LOGGING=true

# CORS
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

---

## 🔌 API Endpoints

### Health & Status

#### `GET /health`
```
Check orchestrator and microservices health status.

Response:
{
  "status": "healthy|degraded|unhealthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "services": {
    "validation": {"healthy": true},
    "backend_api": {"healthy": true},
    "microservice_db": {"healthy": true}
  }
}
```

#### `GET /status`
```
Get detailed orchestrator status.

Response:
{
  "service": "ms_orchestrator",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00",
  "services": {...}
}
```

### Validation Orchestration

#### `POST /orchestrate/validation/validate`
```
Validate a process with automatic context gathering.

Request:
{
  "process_description": "Docente evaluando estudiantes",
  "rules_context": {"course_id": "123"},
  "metadata": {"source": "escalafon_system"}
}

Response:
{
  "status": "success",
  "data": {...},
  "request_id": "uuid-1234"
}
```

#### `POST /orchestrate/validation/validate-batch`
```
Batch validation of multiple processes.

Request:
[
  {"process_description": "...", ...},
  {"process_description": "...", ...}
]

Response:
{
  "status": "success",
  "data": {"items": [...], "count": 2},
  "request_id": "uuid-1234"
}
```

### Workflow Orchestration

#### `POST /orchestrate/workflows/execute`
```
Execute a complex multi-step workflow.

Request:
{
  "workflow_id": "wf_789",
  "workflow_name": "Teacher Evaluation Pipeline",
  "parallel": false,
  "steps": [
    {
      "service": "validation",
      "action": "validate_process",
      "parameters": {...}
    },
    {
      "service": "backend_api",
      "action": "analyze_content",
      "parameters": {...}
    }
  ]
}

Response:
{
  "workflow_id": "wf_789",
  "execution_id": "exec_uuid",
  "status": "completed|running|failed",
  "results": [...],
  "errors": [...],
  "started_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:30:05"
}
```

#### `GET /orchestrate/workflows/templates`
```
Get available workflow templates.

Response:
{
  "status": "success",
  "data": {
    "teacher_evaluation": {...},
    "document_processing": {...},
    ...
  }
}
```

---

## 💡 Uso

### Simple Validation with Context

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/orchestrate/validation/validate",
        json={
            "process_description": "Docente evaluando desempeño académico",
            "rules_context": {"course_id": "MATH101", "semester": "2024-1"},
            "metadata": {"source": "escalafon_web"}
        }
    )
    result = response.json()
    print(result)
```

### Execute Complex Workflow

```python
workflow = {
    "workflow_id": "wf_teacher_eval",
    "workflow_name": "Teacher Evaluation Pipeline",
    "parallel": False,
    "steps": [
        {
            "service": "validation",
            "action": "validate_process",
            "parameters": {
                "process_description": "Evaluación docente",
                "rules_context": {"type": "teaching"}
            }
        },
        {
            "service": "backend_api",
            "action": "analyze_content",
            "parameters": {
                "content": "Análisis de desempeño",
                "analysis_type": "rag"
            }
        },
        {
            "service": "database",
            "action": "store",
            "parameters": {
                "collection": "evaluations",
                "data": {"type": "evaluation", "status": "completed"}
            }
        }
    ]
}

response = await client.post(
    "http://localhost:8000/orchestrate/workflows/execute",
    json=workflow
)
execution = response.json()
```

### Parallel Execution

```python
workflow = {
    "workflow_id": "wf_parallel",
    "workflow_name": "Parallel Analysis",
    "parallel": True,  # Enable parallel execution
    "steps": [
        {"service": "backend_api", "action": "analyze_content", ...},
        {"service": "validation", "action": "validate_process", ...},
        {"service": "database", "action": "query_results", ...}
    ]
}
```

---

## 🛡️ Patrón de Resiliencia

### Circuit Breaker Pattern

```
CLOSED ──[failures ≥ threshold]──> OPEN
  ↑                                  ↓
  |                          [recovery timeout]
  └──── HALF_OPEN ──[success]────┘
        [failure]
           ↓
          OPEN
```

### Retry Logic with Exponential Backoff

```
Request
  ↓
Attempt 1 → [Fail]
  ↓
Wait 1s (initial_delay)
  ↓
Attempt 2 → [Fail]
  ↓
Wait 2s (initial_delay × backoff_factor^1)
  ↓
Attempt 3 → [Fail]
  ↓
Raise RetryExhaustedError
```

### Configuration Example

```python
RETRY_MAX_ATTEMPTS = 3              # 3 total attempts
RETRY_INITIAL_DELAY = 1.0           # 1 second initial wait
RETRY_BACKOFF_FACTOR = 2.0          # Double the wait each time

CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5   # Open after 5 failures
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60   # Try recovery after 60s
```

---

## 📊 Ejemplos

### Example 1: Validate Teacher Process

```bash
curl -X POST http://localhost:8000/orchestrate/validation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "process_description": "Docente de Matemáticas evaluando quiz final",
    "rules_context": {
      "course_id": "MAT101",
      "semester": "2024-1",
      "evaluation_type": "summative"
    },
    "metadata": {"source": "escalafon_web", "user_id": "prof_123"}
  }'
```

### Example 2: Execute Teacher Evaluation Workflow

```bash
curl -X POST http://localhost:8000/orchestrate/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "wf_eval_123",
    "workflow_name": "Complete Teacher Evaluation",
    "parallel": false,
    "steps": [
      {
        "service": "validation",
        "action": "validate_process",
        "parameters": {
          "process_description": "Docente evaluando estudiantes",
          "rules_context": {"evaluation_type": "formative"}
        }
      },
      {
        "service": "backend_api",
        "action": "analyze_content",
        "parameters": {
          "content": "Análisis de resultados de evaluación",
          "analysis_type": "rag"
        }
      },
      {
        "service": "database",
        "action": "store",
        "parameters": {
          "collection": "teacher_evaluations",
          "data": {
            "teacher_id": "prof_123",
            "evaluation_date": "2024-01-15",
            "status": "completed"
          }
        }
      }
    ]
  }'
```

### Example 3: Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:45.123456",
  "services": {
    "validation": {"healthy": true},
    "backend_api": {"healthy": true},
    "microservice_db": {"healthy": true}
  }
}
```

---

## 🔍 Troubleshooting

### Issue: Service Unavailable

**Problem:** `ServiceUnavailableError: Service 'ms_validation' is unavailable`

**Solution:**
1. Verify service is running: `docker ps | grep escalafon_validation`
2. Check service logs: `docker logs escalafon_validation`
3. Verify network connectivity: `docker network ls`
4. Check DNS resolution: `nslookup validation` (inside container)

### Issue: Circuit Breaker Open

**Problem:** `CircuitBreakerOpenError: Circuit breaker for 'ms_validation' is open`

**Solution:**
1. The service has been unavailable for too long
2. Fix the underlying service issue first
3. Wait for recovery timeout (default 60s) or manually restart service
4. Check Circuit Breaker settings in `.env`

### Issue: Timeout Errors

**Problem:** `ServiceTimeoutError: Service 'backend_api' request timed out`

**Solution:**
1. Increase timeout: `SERVICE_TIMEOUT=60`
2. Check if service is performing heavy operations
3. Review service logs for bottlenecks
4. Consider increasing retry attempts: `RETRY_MAX_ATTEMPTS=5`

### Debug Logging

Enable verbose logging:
```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=text  # More readable format
```

Check request tracing with `X-Request-ID` header:
```bash
curl -H "X-Request-ID: debug-123" http://localhost:8000/health
```

Look for `debug-123` in logs to track request through all services.

---

## 📚 Referencias

### Framework & Libraries
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [HTTPX Documentation](https://www.python-httpx.org/)

### Patterns
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

### Related Services
- [ms_validation](../ms_validation/README.md)
- [ia_service_core](../backend_api/README.md)
- [microservice_db](../microservice_db/README.md)

---

## 📄 Licencia

This project is part of the EscalafonIA system and follows the same licensing terms.

---

## 👥 Soporte

For issues, questions, or contributions, please contact the development team or create an issue in the repository.

---

**Last Updated:** January 15, 2024  
**Maintained by:** EscalafonIA Development Team
