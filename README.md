# EscalafonIA Jaguar

Sistema de gestión de escalafón docente, cursos y promociones, con generación de contenido asistida por IA. El repositorio se llama `CinvestavUsicamm`; esta guía está pensada para desarrolladores y responsables de despliegue.

## Contenido

- [Estado del proyecto](#estado-del-proyecto)
- [Características principales](#características-principales)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Configuración](#configuración)
- [Tests](#tests)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Cómo contribuir](#cómo-contribuir)
- [Licencia](#licencia)
- [Limitaciones conocidas y roadmap](#limitaciones-conocidas-y-roadmap)
- [Documentación](#documentación)

## Estado del proyecto

En desarrollo activo. El repositorio incluye la aplicación Django, el stack Docker y la suite de pruebas. Las prioridades y la deuda técnica abierta están en [`PLAN.md`](PLAN.md); antes de un despliegue, revisa también [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Características principales

- Autenticación por sesión y autorización por roles: `ADMIN`, `DOCENTE`, `EVALUADOR` y `GENERADOR`.
- Panel de administración con CRUD de cursos y roles, gestión de usuarios y consulta de tablas de la base de datos.
- Cursos con estados, versionado, contenido JSON y bitácora de auditoría.
- Generación y modificación de cursos con IA mediante Ollama, incluyendo respuestas en streaming.
- Foros y procesos de escalafón/promociones.
- Stack Docker con Nginx, PostgreSQL + pgvector, Redis/Celery, Qdrant, FastAPI y microservicios especializados.

### Arquitectura

- **Django 4.2** (`apps/`): aplicación principal MVT, autenticación, paneles y API interna.
- **`ia_service_core/`**: backend de IA en FastAPI; en el compose se publica como servicio `backend_api` en el puerto `8003`.
- **`ms_orchestrator/`**: orquestador de peticiones en FastAPI, puerto `9000`.
- **PostgreSQL 16 + pgvector**, **Redis** (caché y Celery), **Qdrant** (vectores) y **Ollama** (modelos de IA).
- **Nginx** como proxy inverso en los puertos `80`/`443`.
- El compose raíz es `docker-compose.prod.yml`; algunos microservicios conservan su propio compose para desarrollo aislado.

## Requisitos previos

- Docker Engine o Docker Desktop, con el daemon en ejecución.
- Docker Compose v2 (comandos `docker compose`).
- Python 3.12 para desarrollo local y tests.
- Git.
- Para el stack completo con Ollama se recomiendan al menos 8 GB de RAM (ver [`docs/DEPLOY.md`](docs/DEPLOY.md)).

No hace falta Node: el frontend son plantillas Django y JavaScript servido por Django.

## Instalación

### 1. Clonar y preparar el entorno

```bash
git clone git@github.com:cinvestavusicamm/CinvestavUsicamm.git
cd CinvestavUsicamm
cp .env.example .env
```

### 2. Generar los secretos

Genera dos valores nuevos y pégalos en `.env`:

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
python3 -c "import secrets; print('INTERNAL_SERVICE_KEY=' + secrets.token_urlsafe(48))"
```

`INTERNAL_SERVICE_KEY` debe ser **el mismo valor** para Django y para `ia_service_core`; el compose se niega a arrancar si falta.

Elige la base en `DATABASE_URL` según dónde corras Django:

| Dónde corre Django | `DATABASE_URL` |
|---|---|
| En tu máquina, con el PostgreSQL de Docker | `postgresql://user:password@localhost:5432/cinvestav_db` |
| Dentro del compose (`django`) | El compose lo inyecta solo (`postgres:5432/cinvestav_db`) |
| SQLite local, sin PostgreSQL | Vacío |

Si usas una base remota de forma deliberada en desarrollo, arranca con `ALLOW_REMOTE_DB=1`; el proyecto se niega a usar un host remoto por defecto.

Los cuatro `IA_SERVICE_*` del `.env` apuntan a `http://localhost:8003/...` cuando Django corre en tu máquina. Dentro del compose, el servicio `django` los sobreescribe a `http://backend_api:8003/...`.

### 3. Levantar el stack completo

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec django python manage.py migrate
```

El contenedor Django no ejecuta migraciones automáticamente; el segundo comando es necesario. La primera vez, Ollama descarga `llama3.2:3b` y `nomic-embed-text`, lo que puede tardar varios minutos.

Comprueba que está listo:

```bash
curl -f http://localhost/health/
curl -f http://localhost:8003/health
docker compose -f docker-compose.prod.yml ps
```

### 4. Datos de demostración (opcional)

```bash
docker compose -f docker-compose.prod.yml exec django python manage.py create_initial_data
```

Crea roles, institución, curso y un usuario `ADMIN` de prueba. No lo uses en producción.

### 5. Desarrollo local con Django (opcional)

```bash
python3.12 -m venv venv
./venv/bin/pip install -r apps/requirements.txt
docker compose -f docker-compose.prod.yml up -d postgres redis qdrant ollama backend_api ms_ai_agent_service
./venv/bin/python manage.py migrate
./venv/bin/python manage.py runserver 0.0.0.0:8000
```

## Uso

Con el stack levantado:

- **Aplicación (Nginx):** <http://localhost>
- **Inicio de sesión:** <http://localhost/sesion/>
- **Panel de administración:** <http://localhost/administrador/panel-admin/> (requiere rol `ADMIN`)
- **Django interno:** <http://localhost:8000> (solo si usas `runserver`)
- **Servicio de IA:** <http://localhost:8003/health>
- **Orquestador:** <http://localhost:9000>

Comandos útiles:

```bash
# Logs de Django
docker compose -f docker-compose.prod.yml logs -f django

# Shell de Django
docker compose -f docker-compose.prod.yml exec django python manage.py shell

# Alta interactiva de un ADMIN (solo si aún no existe ninguno y ya hay roles e institución)
docker compose -f docker-compose.prod.yml exec django python manage.py crear_admin_inicial
```

## Configuración

La lista canónica de variables es [`.env.example`](.env.example). Las principales:

| Variable | Uso | Notas |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | Obligatoria; genera una nueva. |
| `DEBUG` | Modo de depuración | `core.settings.dev` y `core.settings.prov` lo fijan en `False`; revisa el settings activo. |
| `DATABASE_URL` | Conexión a la base de datos | Vacío usa SQLite local; el compose inyecta PostgreSQL; `prov.py` rechaza SQLite. |
| `ALLOWED_HOSTS` | Hosts permitidos | En `core.settings.prov` se define una lista explícita; ajústala a tu dominio. |
| `INTERNAL_SERVICE_KEY` | Clave compartida Django ↔ IA | Obligatoria y sin valor por defecto; debe coincidir en ambos lados. |
| `IA_SERVICE_*` | Endpoints del servicio de IA | Cuatro URLs; en local apuntan a `localhost:8003` y el compose las cambia a `backend_api:8003`. |
| `IA_SERVICE_TIMEOUT` | Timeout de `/agente-ajax/` | Mantén la cadena Nginx > Django > llamada a la IA. |
| `POSTGRES_*` | Credenciales del PostgreSQL del compose | Cambia los valores por defecto en producción. |
| `ALLOW_REMOTE_DB` | Permitir base remota en desarrollo | Exporta `1` solo si es deliberado. |

Archivos relevantes:

- `.env.example`: plantilla de configuración.
- `docker-compose.prod.yml`: stack completo.
- `apps/Dockerfile` y `apps/requirements.txt`: imagen y dependencias de Django.
- `core/settings/base.py`, `core/settings/dev.py` y `core/settings/prov.py`: configuración por entorno.
- `nginx/`: configuración del proxy inverso.
- `PLAN.md`: prioridades, deuda técnica y criterios de terminado.

Los settings por defecto de `manage.py` y `core/wsgi.py` son `core.settings.dev`. Para producción existe `core.settings.prov`, que se selecciona con `DJANGO_SETTINGS_MODULE=core.settings.prov`. El `docker-compose.prod.yml` actual no define esa variable; revísalo antes de desplegar.

## Tests

La suite es la de Django, en `apps/users/tests`. Se ejecuta completa con:

```bash
DJANGO_SETTINGS_MODULE=core.settings.dev DATABASE_URL=sqlite:///:memory: \
./venv/bin/python manage.py test
```

`DJANGO_SETTINGS_MODULE` y `DATABASE_URL` se pueden omitir si `manage.py` ya los tiene por defecto y `.env` apunta a una base local; la base en memoria evita tocar ninguna.

Un subconjunto se corre por etiqueta:

```bash
./venv/bin/python manage.py test apps.users.tests.test_admin_protection
```

Un test aparece como `skipped` en SQLite y no es un fallo: `test_admin_protection_concurrency` comprueba `select_for_update`, que SQLite no implementa. Necesita PostgreSQL; el comando está en `PLAN.md`, DEUDA-6.

El repositorio no incluye un workflow de CI en `.github/workflows`; las verificaciones se ejecutan localmente.

## Estructura del proyecto

```text
CinvestavUsicamm/
├── apps/                 # Django: modelos, vistas, servicios, API, rutas y tests
├── core/                 # settings, URLs y WSGI de Django
├── templates/            # plantillas Django
├── static/               # CSS, JavaScript e imágenes
├── ia_service_core/      # backend de IA (FastAPI; servicio backend_api)
├── ms_orchestrator/      # orquestador (FastAPI)
├── ms_*/                 # microservicios especializados
├── infrastructure/       # scripts de inicialización de PostgreSQL/pgvector
├── nginx/                # proxy inverso
├── docs/                 # documentación técnica
└── docker-compose.prod.yml
```

## Cómo contribuir

1. Crea una rama para tu cambio:

   ```bash
   git switch -c feature/mi-cambio
   ```

2. Ejecuta la suite de tests que corresponda:

   ```bash
   ./venv/bin/python manage.py test
   ```

3. Instala y ejecuta los hooks de pre-commit (black, ruff y bandit):

   ```bash
   ./venv/bin/pip install pre-commit
   ./venv/bin/pre-commit install
   ./venv/bin/pre-commit run --all-files
   ```

4. Abre un Pull Request usando [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).

No subas `.env`, credenciales ni tokens. Para reportar problemas o solicitar ayuda, abre un issue en el repositorio.

## Licencia

Este proyecto se distribuye bajo la GNU General Public License v3.0. Consulta [LICENSE](LICENSE).

## Limitaciones conocidas y roadmap

- La deuda técnica y las prioridades abiertas están en [`PLAN.md`](PLAN.md), incluyendo la deriva de migraciones (DEUDA-3).
- El test de concurrencia se omite con SQLite y requiere PostgreSQL para ejecutarse de verdad.
- `docker-compose.prod.yml` no fija `DJANGO_SETTINGS_MODULE=core.settings.prov`; conviene revisarlo antes de un despliegue real.
- TODO: añadir un pipeline de CI que ejecute tests y linters.
- TODO: documentar el alta segura del primer `ADMIN` en producción sin depender de los datos de demostración.
- El stack completo depende de Ollama y de la descarga inicial de modelos; no es un entorno ligero.

## Documentación

- [Documentación general](docs/README.md)
- [API](docs/API.md)
- [Modelos](docs/MODELS.md)
- [Arquitectura](docs/ARCHITECTURE.md)
- [Despliegue](docs/DEPLOY.md)
- [Plan de finalización y deuda técnica](PLAN.md)
