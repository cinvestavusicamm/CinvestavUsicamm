# System Architecture - EscalafonIA Jaguar

## Overview

EscalafonIA Jaguar is a microservices-based system for managing teacher career advancement (escalafón), courses, and AI-powered content generation. The system follows a hexagonal architecture pattern with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  (Web Browser - Django Templates + JavaScript)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
│              (MS Orchestrator - FastAPI)                        │
│  - Request routing                                              │
│  - Circuit breaker                                              │
│  - Retry logic                                                  │
│  - API key validation                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Django     │  │  FastAPI     │  │  PostgreSQL  │
│   Backend    │  │  Backend     │  │  + pgvector  │
│              │  │  (IA Service)│  │              │
│  - Users     │  │  - Ollama    │  │  - Users     │
│  - Courses   │  │  - Embeddings│  │  - Courses   │
│  - Forums    │  │  - Generation│  │  - Forums    │
│  - Escalafón │  │              │  │  - Vectors   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┴────────────────┘
                         │
                ┌────────▼────────┐
                │  Ollama (AI)    │
                │  - phi3:mini    │
                │  - Embeddings   │
                └─────────────────┘
```

---

## MVT Architecture (Django)

### Model Layer

**Location**: `apps/users/models/`

The Model layer represents the database schema and business entities:

- **Purpose**: Data persistence and business rules
- **Technology**: Django ORM with PostgreSQL
- **Pattern**: Active Record pattern
- **Key Models**:
  - `Usuario`: User authentication and profile
  - `Curso`: Course content and metadata
  - `Foro`, `PostForo`: Discussion forums
  - `ProcesoEscalafon`: Career advancement processes
  - `BitacoraEvento`: Audit trail

**Characteristics**:
- Uses `managed = False` for existing database tables
- Implements custom methods for business logic
- Foreign key relationships with CASCADE and PROTECT
- JSONField for flexible data storage

### View Layer

**Location**: `apps/users/views/`

The View layer handles HTTP requests and orchestrates business logic:

- **Purpose**: Request handling and response formatting
- **Technology**: Django function-based views
- **Pattern**: MVC Controller pattern
- **Key View Modules**:
  - `auth_views.py`: Authentication (login, register, logout)
  - `dashboard_views.py`: Main dashboard
  - `docentes/`: Teacher-specific views
  - `generador_cursos/`: Course generator views
  - `evaluador/`: Evaluator views
  - `administrador/`: Admin views
  - `api/`: API endpoints for microservices

**Characteristics**:
- Role-based access control via `@requiere_rol` decorator
- CSRF exemption for API endpoints
- JSON responses for AJAX/API calls
- Session-based authentication

### Template Layer

**Location**: `templates/`

The Template layer renders HTML responses:

- **Purpose**: User interface presentation
- **Technology**: Django Template Language (DTL)
- **Pattern**: Template inheritance
- **Key Template Directories**:
  - `docente/`: Teacher interface
  - `generador_cursos/`: Course generator interface
  - `evaluador/`: Evaluator interface
  - `administrador/`: Admin interface

**Characteristics**:
- Template inheritance with base templates
- Context processors for global data
- Dynamic data rendering from Django context
- JavaScript for client-side interactivity

---

## Service Layer Architecture

### Service Pattern

**Location**: `apps/users/services/`

The Service layer encapsulates business logic and data access:

- **Purpose**: Business logic abstraction and data access
- **Technology**: Python classes with static methods
- **Pattern**: Service Layer pattern
- **Key Services**:
  - `UserService`: User CRUD and authentication
  - `CursoService`: Course management
  - `ForoService`: Forum operations
  - `ProcesoEscalafonService`: Escalafón process management
  - `BitacoraService`: Audit logging
  - `VistasBdService`: Context building for views

**Example Service Structure**:
```python
class CursoService:
    @staticmethod
    def crear_curso(titulo, descripcion, docente_id, estado, generado_con_ia):
        # Business logic for course creation
        # Validation
        # Database operations
        # Audit logging
        return curso
    
    @staticmethod
    def obtener_curso_por_id(curso_id):
        # Retrieve course with error handling
        return curso
```

**Benefits**:
- Separation of concerns
- Reusable business logic
- Easier testing
- Transaction management

---

## Repository Layer Architecture

### Repository Pattern

**Location**: `apps/users/repositories/`

The Repository layer abstracts database operations:

- **Purpose**: Data access abstraction
- **Technology**: Django ORM wrapper
- **Pattern**: Repository pattern
- **Key Repositories**:
  - `UsuarioRepository`: User data access
  - `CursoRepository`: Course data access
  - Generic repository for common operations

**Characteristics**:
- Abstracts Django ORM calls
- Provides query methods
- Handles database-specific logic

---

## API Layer Architecture

### Django API Endpoints

**Location**: `apps/users/api/`

The API layer provides RESTful endpoints for microservices:

- **Purpose**: External API for microservices
- **Technology**: Django views with JSON responses
- **Pattern**: API Gateway pattern
- **Key API Modules**:
  - `usuarios.py`: User management API
  - `cursos.py`: Course management API
  - `foros_api.py`: Forum management API
  - `health.py`: Health check endpoint

**API Characteristics**:
- CSRF exemption for microservice communication
- Rate limiting for sensitive operations
- JSON request/response format
- Role-based access control

---

## Microservices Architecture

### Service Components

#### 1. Django Backend (Main Application)

**Container**: `escalafon_django`
**Port**: 8001 (external), 8000 (internal)
**Technology**: Django 6.0, Gunicorn, Gevent

**Responsibilities**:
- User authentication and authorization
- Course management
- Forum management
- Escalafón process tracking
- Audit logging
- Template rendering

**Dependencies**:
- PostgreSQL database
- FastAPI backend (for AI features)
- MS Orchestrator (for request routing)

---

#### 2. FastAPI Backend (AI Service)

**Container**: `ia_service_core`
**Port**: 8003
**Technology**: FastAPI, Python 3.12

**Responsibilities**:
- AI-powered course generation
- Text embedding generation
- Semantic search
- Document processing
- Ollama integration

**Dependencies**:
- PostgreSQL database
- Ollama service

**Key Features**:
- Health check endpoint
- Async request handling
- Vector similarity search

---

#### 3. MS Orchestrator (Request Orchestrator)

**Container**: `escalafon_orchestrator`
**Port**: 9000
**Technology**: FastAPI, Python

**Responsibilities**:
- Request routing and load balancing
- Circuit breaker pattern
- Retry logic with exponential backoff
- API key validation
- Request/response logging
- CORS handling

**Configuration**:
- Service timeout: 30s
- Connection timeout: 10s
- Retry attempts: 3
- Circuit breaker threshold: 5 failures
- Circuit breaker recovery timeout: 60s

---

#### 4. PostgreSQL Database

**Container**: `escalafon_db`
**Port**: 5432
**Technology**: PostgreSQL 16 + pgvector

**Responsibilities**:
- Persistent data storage
- Vector similarity search (pgvector)
- Transaction management
- Data integrity

**Key Features**:
- Health check endpoint
- Automatic backups (via volumes)
- pgvector extension for AI features

---

#### 5. Ollama AI Engine

**Container**: `motor_ollama`
**Port**: 11434
**Technology**: Ollama

**Responsibilities**:
- Text generation (phi3:mini model)
- Embedding generation
- AI inference

**Configuration**:
- Model: phi3:mini
- Keep alive: 24 hours

---

## Request Flow

### Typical Web Request Flow

```
1. User Action (Browser)
   ↓
2. HTTP Request to Django (localhost:8001)
   ↓
3. Django URL Routing (core/urls.py)
   ↓
4. Middleware Processing
   - SecurityMiddleware
   - SessionMiddleware
   - CsrfViewMiddleware
   - AuthenticationMiddleware
   ↓
5. View Function (apps/users/views/)
   ↓
6. Service Layer (apps/users/services/)
   ↓
7. Repository Layer (apps/users/repositories/)
   ↓
8. Django ORM → PostgreSQL
   ↓
9. Response Processing
   - Serializer (apps/users/serializers/)
   - Context Building
   ↓
10. Template Rendering (templates/)
    ↓
11. HTTP Response to Browser
```

### API Request Flow (Microservices)

```
1. External Service Request
   ↓
2. MS Orchestrator (localhost:9000)
   - API Key Validation
   - Rate Limiting Check
   - Circuit Breaker Check
   ↓
3. Request Routing
   - To Django Backend (localhost:8000)
   - To FastAPI Backend (localhost:8003)
   ↓
4. Service Processing
   - Business Logic
   - Database Operations
   ↓
5. Response
   - Success/Failure
   - Retry if needed
   ↓
6. Response to External Service
```

### AI-Powered Course Generation Flow

```
1. User requests course generation (Django)
   ↓
2. Django calls FastAPI Backend
   ↓
3. FastAPI calls Ollama for content generation
   ↓
4. Ollama generates course structure
   - Modules
   - Questions
   - Activities
   ↓
5. FastAPI processes and validates content
   ↓
6. FastAPI stores embeddings in PostgreSQL (pgvector)
   ↓
7. FastAPI returns content to Django
   ↓
8. Django saves course to database
   ↓
9. Django renders course in template
```

---

## Django Apps Structure

### apps/users

**Purpose**: Main application for user management and core functionality

**Subdirectories**:
- `models/`: Data models
- `views/`: View functions organized by role
  - `docentes/`: Teacher views
  - `generador_cursos/`: Course generator views
  - `evaluador/`: Evaluator views
  - `administrador/`: Admin views
- `services/`: Business logic layer
- `repositories/`: Data access layer
- `api/`: API endpoints
- `routes/`: URL configuration by role
- `serializers/`: Data serialization
- `forms/`: Django forms
- `validators/`: Custom validators
- `config/`: Configuration and constants
- `infrastructure/`: Infrastructure components
- `utils/`: Utility functions

**Role-Based URL Routing**:
- `/administrador/*`: Admin routes
- `/docente/*`: Teacher routes
- `/generador/*`: Course generator routes
- `/evaluador/*`: Evaluator routes

---

## Complex Business Flows

### 1. User Registration and Role Assignment

**Flow**:
1. User submits registration form
2. Django validates input (email uniqueness, CURP format)
3. UserService creates user with hashed password
4. User assigned to default role (or specified role)
5. User assigned to institution
6. BitacoraService logs registration event
7. Session created for user
8. Redirect to dashboard based on role

**Key Components**:
- `auth_views.py`: Registration view
- `UserService`: User creation logic
- `BitacoraService`: Audit logging
- `@requiere_rol`: Role-based access control

**Error Handling**:
- Duplicate email/CURP → 400 error
- Invalid role/institution → 400 error
- Database error → 500 error

---

### 2. Course Creation with AI

**Flow**:
1. User (Generador role) requests course generation
2. Django validates user permissions
3. Django calls FastAPI backend with course parameters
4. FastAPI calls Ollama for content generation
5. Ollama generates course structure using phi3:mini
6. FastAPI validates and formats content
7. FastAPI generates embeddings for semantic search
8. FastAPI stores embeddings in PostgreSQL (pgvector)
9. FastAPI returns structured content to Django
10. Django creates Curso record with contenido_json
11. Django creates RetroalimentacionIaCurso record
12. BitacoraService logs course creation
13. Django renders course in template

**Key Components**:
- `generador_de_cursos.py`: Course generation view
- `CursoService`: Course creation logic
- FastAPI backend: AI processing
- Ollama: Content generation
- pgvector: Embedding storage

**Error Handling**:
- AI service unavailable → Fallback to manual creation
- Invalid content → Validation error
- Database error → Rollback transaction

---

### 3. Escalafón Process Evaluation

**Flow**:
1. Teacher submits escalafón process
2. Django validates process data (CURP, institution, function)
3. ProcesoEscalafonService creates process record
4. Multifactor evaluation data stored as JSON
5. Evaluator reviews process
6. Evaluator provides feedback and decision
7. ProcesoAprobacionCursosService creates approval record
8. Process status updated (Aprobado/Rechazado/Observaciones)
9. BitacoraService logs evaluation
10. Teacher notified of decision
11. Process moves to next stage if approved

**Key Components**:
- `ProcesoEscalafonService`: Process management
- `ProcesoAprobacionCursosService`: Approval workflow
- `BitacoraService`: Audit trail
- `ProcesoEscalafon` model: Process data
- `ProcesoAprobacionCursos` model: Approval tracking

**Error Handling**:
- Invalid data → Validation error
- Missing required fields → 400 error
- Database constraint violation → 500 error

---

## Security Architecture

### Authentication

- **Method**: Session-based authentication
- **Password Hashing**: Django's default PBKDF2
- **Session Management**: Django sessions with secure cookies
- **Login URL**: `/sesion/`
- **Logout URL**: `/logout/`

### Authorization

- **Method**: Role-based access control (RBAC)
- **Decorator**: `@requiere_rol(ROLE_XXX)`
- **Roles**: Admin, Docente, Generador, Evaluador, Agente
- **Implementation**: Decorator checks session role and redirects if unauthorized

### Security Middleware

1. **SecurityMiddleware**: HSTS, SSL redirect
2. **CsrfViewMiddleware**: CSRF protection
3. **SessionMiddleware**: Session management
4. **AuthenticationMiddleware**: User authentication

### Rate Limiting

- **Implementation**: Django cache-based rate limiting
- **Endpoints**: User creation, user update
- **Configuration**: 10 requests per hour per IP
- **Storage**: Django cache backend

### Audit Logging

- **Implementation**: BitacoraEvento model
- **Events Tracked**: User creation, updates, login, course operations
- **Data Stored**: User ID, event type, description, timestamp, IP address, details (JSON)
- **Log Files**: `logs/security.log`, `logs/error.log`

---

## Data Flow Architecture

### Database Access Pattern

```
View → Service → Repository → Django ORM → PostgreSQL
```

**Benefits**:
- Separation of concerns
- Testability
- Reusability
- Transaction management

### Caching Strategy

- **Implementation**: Django cache framework
- **Use Cases**: Rate limiting, session data, frequently accessed data
- **Backend**: Configurable (Redis, Memcached, database)

### Transaction Management

- **Django ORM**: Automatic transaction management
- **Service Layer**: Manual transaction control when needed
- **Rollback**: On error in service methods

---

## Communication Between Services

### Service-to-Service Communication

**Protocol**: HTTP/HTTPS
**Format**: JSON
**Authentication**: API keys (MS Orchestrator)
**Error Handling**: Circuit breaker pattern

### Service Discovery

- **Method**: Hardcoded URLs in docker-compose.yml
- **Future**: Service registry (Consul, etcd)

### Load Balancing

- **Current**: Single instance per service
- **Future**: Nginx or HAProxy

---

## Scalability Considerations

### Horizontal Scaling

- **Django**: Gunicorn with gevent workers (2 workers)
- **FastAPI**: Uvicorn with async support
- **PostgreSQL**: Read replicas (future)
- **Ollama**: Model sharding (future)

### Vertical Scaling

- **Django**: Increase worker count
- **FastAPI**: Increase worker count
- **PostgreSQL**: Increase resources
- **Ollama**: GPU acceleration

### Caching Strategy

- **Session Data**: Django cache
- **API Responses**: Redis (future)
- **Static Files**: WhiteNoise + CDN (future)
- **Database Queries**: Query optimization, indexes

---

## Monitoring and Observability

### Health Checks

- **Django**: `/health/` endpoint
- **FastAPI**: `/health` endpoint
- **Orchestrator**: Health check configured
- **PostgreSQL**: pg_isready command

### Logging

- **Django**: Structured logging (JSON format)
- **Log Files**: `logs/error.log`, `logs/security.log`
- **Log Levels**: INFO, WARNING, ERROR
- **Loggers**: django, utils, security

### Metrics (Future)

- **Implementation**: Prometheus + Grafana
- **Metrics**: Request count, response time, error rate
- **Custom Metrics**: Course creation count, user registrations

---

## Deployment Architecture

### Container Orchestration

- **Tool**: Docker Compose
- **Future**: Kubernetes
- **Configuration**: docker-compose.yml
- **Volumes**: PostgreSQL data, Ollama models, static files

### Environment Configuration

- **Method**: Environment variables (.env file)
- **Management**: python-decouple library
- **Sensitive Data**: SECRET_KEY, database credentials, API keys

### CI/CD Pipeline (Future)

- **Version Control**: Git
- **CI**: GitHub Actions / GitLab CI
- **CD**: Automated deployment to production
- **Testing**: Automated test suite

---

## Technology Stack Summary

### Backend
- **Framework**: Django 6.0
- **Language**: Python 3.12
- **API**: FastAPI (for AI service)
- **ORM**: Django ORM
- **Server**: Gunicorn + Gevent

### Database
- **Engine**: PostgreSQL 16
- **Extension**: pgvector (for AI features)
- **ORM**: Django ORM

### AI/ML
- **Engine**: Ollama
- **Model**: phi3:mini
- **Embeddings**: Custom implementation
- **Vector Search**: pgvector

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: Nginx (future)
- **Load Balancer**: HAProxy (future)

### Frontend
- **Templates**: Django Template Language
- **CSS**: Custom CSS + Tailwind CSS
- **JavaScript**: Vanilla JS + FontAwesome
- **Icons**: FontAwesome 6.4.0

---

## Design Patterns Used

1. **MVC Pattern**: Django's MVT architecture
2. **Service Layer Pattern**: Business logic abstraction
3. **Repository Pattern**: Data access abstraction
4. **Decorator Pattern**: Role-based access control
5. **Factory Pattern**: Serializer creation
6. **Strategy Pattern**: Multiple authentication strategies (future)
7. **Observer Pattern**: Audit logging (signals)
8. **Circuit Breaker Pattern**: MS Orchestrator
9. **Retry Pattern**: MS Orchestrator
10. **Active Record Pattern**: Django ORM

---

## Future Architecture Improvements

1. **API Gateway**: Kong or AWS API Gateway
2. **Message Queue**: RabbitMQ or Kafka for async processing
3. **Caching Layer**: Redis for session and response caching
4. **Search Engine**: Elasticsearch for full-text search
5. **CDN**: CloudFront or Cloudflare for static assets
6. **Monitoring**: Prometheus + Grafana
7. **Tracing**: Jaeger or Zipkin
8. **Service Mesh**: Istio (for Kubernetes)
9. **Event Sourcing**: For audit trail (future)
10. **CQRS**: Separate read/write models (future)
