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

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)
- Git

## 🚀 Inicio Rápido con Docker

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd CinvestavUsicamm
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env` con las configuraciones necesarias.

### 3. Levantar el Proyecto

```bash
cd infrastructure
docker-compose up --build -d
```

### 4. Ejecutar Migraciones

```bash
docker-compose exec django python manage.py migrate
```

### 5. Verificar el Sistema

- **Django**: http://localhost:8001
- **FastAPI**: http://localhost:8003
- **Health Check**: http://localhost:8001/health/

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
