# EscalafonIA Jaguar - Sistema de Gestión de Escalafón Docente

Sistema integral para la gestión de procesos de escalafón, cursos, y promociones docentes con integración de Inteligencia Artificial.

## 🏗️ Arquitectura del Sistema

Este proyecto implementa una arquitectura de microservicios con los siguientes componentes:

- **Django Backend**: Aplicación principal para gestión de usuarios, cursos, foros y procesos de escalafón
- **FastAPI Backend**: Servicio de IA para generación de cursos con Ollama
- **PostgreSQL + pgvector**: Base de datos con soporte para vectores
- **Ollama**: Motor de Inteligencia Artificial para generación de contenido
- **MS Orchestrator**: Microservicio de orquestación de requests

## 📋 Requisitos Previos

- Docker Desktop (con el daemon corriendo) y Docker Compose v2
- Python 3.12
- Git

No hace falta Node: el frontend son plantillas Django y JS servido por Django.

## 🚀 Inicio Rápido

### 1. Clonar y crear el entorno

```bash
git clone <repository-url>
cd CinvestavUsicamm
python3.12 -m venv venv
./venv/bin/pip install -r apps/requirements.txt
```

### 2. Configurar `.env`

```bash
cp .env.example .env
```

Genera los dos secretos y pégalos en `.env`:

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
python -c "import secrets; print('INTERNAL_SERVICE_KEY=' + secrets.token_urlsafe(48))"
```

`INTERNAL_SERVICE_KEY` tiene que ser **el mismo valor** para Django y para
`ia_service_core`; los compose se niegan a arrancar si falta.

Elige la base en `DATABASE_URL` según dónde corras Django:

| Dónde corre Django | `DATABASE_URL` |
|---|---|
| En tu máquina, con el Postgres de Docker | `postgresql://user:password@localhost:5432/cinvestav_db` |
| Dentro del compose (`django`) | el compose lo inyecta solo (`postgres:5432/cinvestav_db`) |
| SQLite local (sin Postgres) | vacío |

Si usas una base remota (p. ej. Supabase), arranca con
`ALLOW_REMOTE_DB=1`; el proyecto se niega a usar un host remoto por defecto.

Los cuatro `IA_SERVICE_*` del `.env` apuntan a `http://localhost:8003/...` para
cuando corras Django en tu máquina. Dentro del compose, el servicio `django`
los sobreescribe a `http://backend_api:8003/...`.

### 3. Levantar el proyecto

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

La primera vez construye todos los servicios y Ollama descarga
`llama3.2:3b` y `nomic-embed-text` (varios minutos). Comprueba que está listo:

```bash
curl http://localhost:8003/health
docker compose -f docker-compose.prod.yml ps
```

### 4. Desarrollar con Django en tu máquina (opcional)

Si prefieres `runserver` en vez de reconstruir la imagen de Django, levanta solo
la infraestructura y corre Django contra ella:

```bash
docker compose -f docker-compose.prod.yml up -d postgres redis qdrant ollama backend_api ms_ai_agent_service
./venv/bin/python manage.py migrate
./venv/bin/python manage.py runserver 0.0.0.0:8000
```

### 5. Verificar el Sistema

- **Aplicación** (nginx): http://localhost
- **Django** interno: http://localhost:8000 (solo si lo arrancas en tu máquina)
- **Servicio de IA**: http://localhost:8003/health
- **Orquestador**: http://localhost:9000

`docker-compose.prod.yml` es el único compose del proyecto: levanta Django,
Postgres, Redis, Qdrant, Ollama, `ia_service_core` y los microservicios.

## 🧪 Pruebas

La suite es la de Django, en `apps/users/tests`. Corre entera con:

```bash
DJANGO_SETTINGS_MODULE=core.settings.dev DATABASE_URL=sqlite:///:memory: \
./venv/bin/python manage.py test
```

`DJANGO_SETTINGS_MODULE` y `DATABASE_URL` se pueden omitir si `manage.py` ya los tiene por defecto y
`.env` apunta a una base de datos local; la base en memoria evita tocar ninguna.

Un subconjunto se corre por etiqueta:

```bash
./venv/bin/python manage.py test apps.users.tests.test_admin_protection
```

Un test aparece como `skipped` en SQLite y no es un fallo: `test_admin_protection_concurrency`
comprueba `select_for_update`, que SQLite no implementa. Necesita PostgreSQL; el comando está en
`PLAN.md`, DEUDA-6.

## 📚 Documentación Completa

Para documentación técnica detallada, consulta la carpeta `/docs`:

- [Documentación de API](docs/API.md)
- [Documentación de Modelos](docs/MODELS.md)
- [Arquitectura del Sistema](docs/ARCHITECTURE.md)
- [Guía de Despliegue](docs/DEPLOY.md)
