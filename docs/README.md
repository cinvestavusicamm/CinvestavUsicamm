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

Copiar el archivo de ejemplo de variables de entorno:

```bash
cp .env.example .env
```

Editar el archivo `.env` con las configuraciones necesarias:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/escalafon_db
ALLOWED_HOSTS=localhost,127.0.0.1

# Microservices URLs
VALIDATION_SERVICE_URL=http://localhost:8001
BACKEND_API_URL=http://localhost:8003
MICROSERVICE_DB_URL=http://localhost:8002
DJANGO_BACKEND_URL=http://localhost:8000
```

**Variables de Entorno Obligatorias:**

- `SECRET_KEY`: Clave secreta de Django (cambiar en producción)
- `DATABASE_URL`: URL de conexión a PostgreSQL
- `DEBUG`: Modo de depuración (False en producción)
- `ALLOWED_HOSTS`: Hosts permitidos para el servidor

### 3. Levantar el Proyecto con Docker Compose

```bash
cd infrastructure
docker-compose up --build -d
```

Este comando:
- Construye todas las imágenes Docker
- Inicia PostgreSQL con pgvector
- Inicia el motor de IA Ollama
- Inicia el backend FastAPI
- Inicia la aplicación Django
- Inicia el microservicio de orquestación

### 4. Ejecutar Migraciones

Las migraciones se ejecutan automáticamente al iniciar el contenedor Django. Si necesitas ejecutarlas manualmente:

```bash
docker-compose exec django python manage.py migrate
```

### 5. Verificar que el Sistema Funciona

- **Django Backend**: http://localhost:8001
- **FastAPI Backend**: http://localhost:8003
- **MS Orchestrator**: http://localhost:9000
- **Health Check**: http://localhost:8001/health/
- **Admin Panel**: http://localhost:8001/admin/

## 📁 Estructura del Proyecto

```
CinvestavUsicamm/
├── apps/                    # Aplicación Django principal
│   ├── users/              # App de usuarios
│   │   ├── models/         # Modelos de datos
│   │   ├── views/          # Vistas y controladores
│   │   ├── services/       # Lógica de negocio
│   │   ├── api/            # Endpoints API
│   │   ├── routes/         # Configuración de URLs
│   │   └── serializers/    # Serializadores
│   ├── Dockerfile
│   └── requirements.txt
├── backend_api/            # Backend FastAPI (IA)
├── ms_orchestrator/        # Microservicio de orquestación
├── infrastructure/         # Configuración Docker
│   └── docker-compose.yml
├── core/                   # Configuración central de Django
│   ├── settings/           # Settings de Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI configuration
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos
├── docs/                   # Documentación
├── Dockerfile              # Dockerfile principal
├── manage.py              # Script de gestión Django
└── .env.example           # Ejemplo de variables de entorno
```

## 🔧 Comandos Útiles de Docker

### Ver Logs de Todos los Servicios

```bash
docker-compose logs -f
```

### Ver Logs de un Servicio Específico

```bash
docker-compose logs -f django
docker-compose logs -f backend
docker-compose logs -f db
```

### Detener Todos los Servicios

```bash
docker-compose down
```

### Detener y Eliminar Volúmenes

```bash
docker-compose down -v
```

### Reconstruir un Servicio Específico

```bash
docker-compose up --build -d django
```

### Ejecutar Comandos en el Contenedor Django

```bash
docker-compose exec django python manage.py shell
docker-compose exec django python manage.py createsuperuser
docker-compose exec django python manage.py collectstatic
```

### Acceder a la Base de Datos

```bash
docker-compose exec db psql -U user -d escalafon_db
```

## 🗄️ Base de Datos

El sistema utiliza PostgreSQL con extensión pgvector para almacenamiento de vectores y búsquedas semánticas.

### Configuración de la Base de Datos

- **Motor**: PostgreSQL 16 con pgvector
- **Usuario**: user
- **Contraseña**: password (cambiar en producción)
- **Base de Datos**: escalafon_db
- **Puerto**: 5432

### Migraciones

Las migraciones se gestionan a través de Django. El sistema utiliza tablas existentes (managed=False) por lo que las migraciones son solo para referencia.

## 🔐 Seguridad

### Variables Sensibles

Las siguientes variables deben cambiarse en producción:

- `SECRET_KEY`: Generar una clave segura
- `MICROSERVICE_SECRET`: Clave para comunicación entre microservicios
- `POSTGRES_PASSWORD`: Contraseña de la base de datos

### Configuración de Seguridad en Producción

En el archivo `core/settings/base.py` se deben habilitar las siguientes opciones:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 🧪 Testing

Para ejecutar pruebas:

```bash
docker-compose exec django python manage.py test
```

## 📊 Monitoreo

### Health Checks

- **Django**: http://localhost:8001/health/
- **FastAPI**: http://localhost:8003/health
- **Orchestrator**: http://localhost:9000/health

### Logs

Los logs se almacenan en:
- Django: `logs/error.log`, `logs/security.log`
- Docker: `docker-compose logs`

## 🤝 Contribución

1. Fork el repositorio
2. Crear una rama para la feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia [LICENSE](../LICENSE).

## 📞 Soporte

Para reportar problemas o solicitar ayuda, abrir un issue en el repositorio.

## 🚨 Solución de Problemas Comunes

### El contenedor Django no inicia

Verificar que la base de datos esté lista:

```bash
docker-compose ps
docker-compose logs db
```

### Error de conexión a la base de datos

Verificar las credenciales en `.env` y que el contenedor de base de datos esté corriendo.

### Ollama no responde

Verificar que el modelo phi3:mini esté descargado:

```bash
docker-compose exec ollama ollama list
```

### Migraciones fallidas

Eliminar el volumen de base de datos y volver a crear:

```bash
docker-compose down -v
docker-compose up --build -d
```

## 📚 Documentación Adicional

- [Documentación de API](API.md)
- [Documentación de Modelos](MODELS.md)
- [Arquitectura del Sistema](ARCHITECTURE.md)
- [Guía de Despliegue](DEPLOY.md)
