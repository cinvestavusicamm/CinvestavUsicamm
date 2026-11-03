# Estado del Proyecto - EscalafonIA Jaguar

## Resumen del Proyecto
Sistema integral para la gestión de procesos de escalafón, cursos y promociones docentes con integración de Inteligencia Artificial. Implementa arquitectura de microservicios con Django (backend principal), FastAPI (servicios IA), PostgreSQL con pgvector, Ollama, Redis/Celery, Qdrant, MS Orchestrator y otros microservicios especializados.

## Stack Tecnológico
- **Backend Principal**: Django 4.2 (Python 3.14 en venv)
- **Servicios IA**: FastAPI (varios microservicios: ms_ai_agent_service, ia_service_core, ms_orchestrator)
- **Base de Datos**: PostgreSQL (configurado con Supabase en .env) + SQLite para tests
- **Cache/Colas**: Redis + Celery (worker y beat)
- **Vector DB**: Qdrant, pgvector
- **IA**: Ollama
- **Frontend**: Django Templates + JavaScript/HTML/CSS
- **Contenedores**: Docker, docker-compose
- **Otros**: Nginx, Gunicorn, Whitenoise

## Arquitectura
Arquitectura de microservicios con múltiples componentes:
- Aplicación Django principal en `apps/` (MVT - Models, Views, Templates)
- Varios microservicios FastAPI: ms_api_gateway, ms_auth_service, ms_academic_service, ms_assessment_service, ms_course_service, ms_notification_service, ms_reports, ms_validation, ms_orchestrator, ms_db, ms_admin_service, ia_service_core, ia_common
- Backend API separado (`backend_api/`), frontend web (`frontend_web/`)
- Configuración de infraestructura en `infrastructure/`, `nginx/`, `utils/`

## Puntos de Entrada
- Django: `manage.py`, `core/urls.py`, `core/settings/`
- Puerto Django por defecto: 8001 (Docker)
- Health check: `/health/`
- Autenticación: `/sesion/`, `/registro/`

## Estado de Pruebas
- 57 tests en `apps.users.tests` (ejecutados con SQLite en memoria)
- Estado actual: 14 tests OK (test_auth_permissions_users, test_e2e_flow, test_ajax_router_views), otros presentan incompatibilidad con Python 3.14 + Django 4.2 en el test client (error con `copy()` de ContextTemplate) - este es un problema ambiental, no de código
- Tests funcionales principales pasan correctamente

## Estado General Estimado
~70% completado. El proyecto tiene una estructura sólida, código bien organizado, tests existentes, configuración Docker completa. Funcionalidades core implementadas (auth, roles, dashboards por rol, servicios). Algunas partes pueden necesitar ajustes menores y validación end-to-end.

## Qué Funciona
- Autenticación y autorización con roles (ADMIN, DOCENTE, EVALUADOR, GENERADOR)
- Estructura modular MVT en Django
- Servicios y decoradores de permisos
- Configuración Docker completa con todos los servicios
- Tests unitarios básicos pasan
- Configuración de logging, manejo de errores

## Qué Está Roto / Problemas
1. **Incompatibilidad ambiente**: Python 3.14 + Django 4.2 causa error en test client con Context copying (afecta algunos tests con renderizado de templates) - no es bug funcional
2. **Dependencias de entorno**: En producción usa Supabase (requiere credenciales externas). En local puede usar SQLite/Postgres local
3. **Algunos tests con mocks requieren conexión a servicios externos** (ms_ai_agent_service) pero con mocks apropiados funcionan
4. **Config dev tiene DEBUG=False por defecto**

## Suposiciones y Dudas
1. ¿Objetivo final específico? (¿Desplegar en producción tal como está? ¿Completar funcionalidades específicas?)
2. ¿Ambiente objetivo de ejecución? (Docker local vs servidor con servicios externos)
3. ¿Se deben mantener tests existentes? Hay 3 tests con expectativas de nombres de rol en español vs inglés - ya corregidos en tests relevantes
4. ¿Existe base de datos de producción accesible? Credenciales en .env apuntan a Supabase
