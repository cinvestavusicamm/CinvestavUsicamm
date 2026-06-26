# API Documentation - EscalafonIA Jaguar

## Overview

This document describes all API endpoints available in the EscalafonIA Jaguar system. The system uses Django views with JSON responses for API communication.

## Base URL

- **Development**: `http://localhost:8001`
- **Production**: Configured via `ALLOWED_HOSTS`

## Authentication

Most endpoints require session-based authentication. Users must be logged in via the web interface to access protected endpoints.

## Response Format

All API responses follow this standard format:

```json
{
  "success": true/false,
  "message": "Description",
  "data": {},
  "error": "Error message if applicable"
}
```

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `405 Method Not Allowed`: HTTP method not supported
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Health Check

### GET /health/

Health check endpoint for monitoring.

**Endpoint**: `GET /health/`

**Authentication**: None

**Response**:
```json
{
  "status": "ok",
  "service": "django_backend",
  "version": "1.0.0"
}
```

**Status Codes**: 200

---

## User Management API

### POST /api/usuarios/agregar/

Create a new user (Admin only).

**Endpoint**: `POST /api/usuarios/agregar/`

**Authentication**: Required (Admin role)

**Request Body** (form-data):
```
nombre: string (required)
apellido_paterno: string (required)
apellido_materno: string (optional)
correo: string (required, unique)
contrasena: string (required)
curp: string (required, unique, max 18 chars)
rol: integer (required, Rol ID)
institucion: integer (required, Institucion ID)
```

**Response**:
```json
{
  "success": true,
  "message": "Usuario agregado correctamente",
  "usuario_id": 123
}
```

**Error Responses**:
- `400`: Missing required fields, invalid field length, duplicate CURP/email, invalid role/institution
- `429`: Rate limit exceeded (max 10 attempts per hour)
- `500`: Internal server error

**Status Codes**: 200, 400, 429, 500

---

### POST /api/usuarios/editar/<int:usuario_id>/

Update an existing user (Admin only).

**Endpoint**: `POST /api/usuarios/editar/<usuario_id>/`

**Authentication**: Required (Admin role)

**Request Body** (form-data):
```
nombre: string (optional)
apellido_paterno: string (optional)
apellido_materno: string (optional)
correo: string (optional)
curp: string (optional)
rol: integer (optional)
institucion: integer (optional)
contrasena: string (optional)
contrasena_actual: string (required if changing password)
```

**Response**:
```json
{
  "success": true,
  "message": "Usuario actualizado correctamente"
}
```

**Error Responses**:
- `400`: Invalid field length, invalid role/institution, missing current password
- `404`: User not found
- `429`: Rate limit exceeded
- `500`: Internal server error

**Status Codes**: 200, 400, 404, 429, 500

---

### POST /api/usuarios/toggle/<int:usuario_id>/

Activate/deactivate a user (Admin only).

**Endpoint**: `POST /api/usuarios/toggle/<usuario_id>/`

**Authentication**: Required (Admin role)

**Request Body**: None

**Response**:
```json
{
  "success": true,
  "message": "Usuario desactivado correctamente",
  "activo": false,
  "contadores": {
    "total": 100,
    "activos": 99
  }
}
```

**Error Responses**:
- `400`: Cannot deactivate own account
- `404`: User not found

**Status Codes**: 200, 400, 404

---

### GET /api/usuarios/<int:usuario_id>/

Get user details by ID (Admin only).

**Endpoint**: `GET /api/usuarios/<usuario_id>/`

**Authentication**: Required (Admin role)

**Response**:
```json
{
  "success": true,
  "id_usuario": 123,
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "López",
  "correo": "juan@example.com",
  "curp": "PERJ800101HDFXXX01",
  "rol": 1,
  "institucion": 1
}
```

**Error Responses**:
- `404`: User not found
- `500`: Internal server error

**Status Codes**: 200, 404, 500

---

## Course Management API

### GET /api/cursos/listar/

List all courses or filter by teacher.

**Endpoint**: `GET /api/cursos/listar/`

**Authentication**: Required

**Query Parameters**:
```
docente_id: integer (optional) - Filter courses by teacher ID
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id_curso": 1,
      "titulo": "Curso de Matemáticas",
      "descripcion": "Descripción del curso",
      "estado": "Aprobado",
      "generado_con_ia": true,
      "version": 1,
      "fecha_creacion": "2024-01-01T00:00:00Z",
      "fecha_aprobacion": "2024-01-15T00:00:00Z",
      "docente_id": 123
    }
  ],
  "count": 1
}
```

**Status Codes**: 200

---

### POST /api/cursos/crear/

Create a new course (Generator role only).

**Endpoint**: `POST /api/cursos/crear/`

**Authentication**: Required (Generator role)

**Request Body** (JSON):
```json
{
  "titulo": "string (required)",
  "descripcion": "string (optional)",
  "contenido": {
    "modulos": [],
    "preguntas_audio": [],
    "relaciones": [],
    "examen_final": []
  }
}
```

**Response**:
```json
{
  "success": true,
  "mensaje": "Curso creado exitosamente",
  "curso_id": 1,
  "titulo": "Curso de Matemáticas"
}
```

**Error Responses**:
- `400`: Missing title, invalid JSON
- `403`: Permission denied
- `500`: Internal server error

**Status Codes**: 201, 400, 403, 500

---

### POST /api/cursos/actualizar/<int:curso_id>/

Update an existing course (Generator role only).

**Endpoint**: `POST /api/cursos/actualizar/<curso_id>/`

**Authentication**: Required (Generator role)

**Request Body** (JSON):
```json
{
  "titulo": "string (optional)",
  "descripcion": "string (optional)",
  "estado": "string (optional)",
  "contenido": {
    "modulos": [],
    "preguntas_audio": [],
    "relaciones": [],
    "examen_final": []
  }
}
```

**Response**:
```json
{
  "success": true,
  "mensaje": "Curso actualizado exitosamente",
  "curso_id": 1
}
```

**Error Responses**:
- `400`: Invalid JSON
- `403`: Not course owner
- `404`: Course not found
- `500`: Internal server error

**Status Codes**: 200, 400, 403, 404, 500

---

## Forum Management API

### GET /api/foros/listar/

List all forums or filter by course.

**Endpoint**: `GET /api/foros/listar/`

**Authentication**: Required

**Query Parameters**:
```
curso_id: integer (optional) - Filter forums by course ID
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id_foro": 1,
      "curso_id": 1,
      "titulo": "Foro de Discusión",
      "descripcion": "Descripción del foro",
      "fecha_creacion": "2024-01-01T00:00:00Z",
      "activo": true
    }
  ],
  "count": 1
}
```

**Status Codes**: 200

---

## Docente Role Endpoints

### POST /docente/api/crear-curso/

Create a course from docente panel.

**Endpoint**: `POST /docente/api/crear-curso/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
titulo: string (required)
descripcion: string (optional)
estado: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Curso creado exitosamente",
  "curso_id": 1
}
```

**Status Codes**: 200, 400, 403

---

### POST /docente/api/actualizar-curso/<int:curso_id>/

Update a course from docente panel.

**Endpoint**: `POST /docente/api/actualizar-curso/<curso_id>/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
titulo: string (optional)
descripcion: string (optional)
estado: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Curso actualizado exitosamente"
}
```

**Status Codes**: 200, 400, 403, 404

---

### POST /docente/api/eliminar-curso/<int:curso_id>/

Delete a course from docente panel.

**Endpoint**: `POST /docente/api/eliminar-curso/<curso_id>/`

**Authentication**: Required (Docente role)

**Response**:
```json
{
  "success": true,
  "message": "Curso eliminado exitosamente"
}
```

**Status Codes**: 200, 400, 403, 404

---

### POST /docente/api/crear-foro/

Create a new forum.

**Endpoint**: `POST /docente/api/crear-foro/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
curso_id: integer (required)
titulo: string (required)
descripcion: string (required)
```

**Response**:
```json
{
  "success": true,
  "message": "Foro creado exitosamente",
  "foro_id": 1
}
```

**Status Codes**: 200, 400, 403

---

### POST /docente/api/crear-post/

Create a new forum post.

**Endpoint**: `POST /docente/api/crear-post/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
foro_id: integer (required)
contenido: string (required)
```

**Response**:
```json
{
  "success": true,
  "message": "Post creado exitosamente",
  "post_id": 1
}
```

**Status Codes**: 200, 400, 403, 404

---

### POST /docente/api/actualizar-perfil/

Update docente profile.

**Endpoint**: `POST /docente/api/actualizar-perfil/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
nombre: string (optional)
apellido_paterno: string (optional)
apellido_materno: string (optional)
correo: string (optional)
telefono: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Perfil actualizado exitosamente"
}
```

**Status Codes**: 200, 400

---

### POST /docente/api/actualizar-contrasena/

Change docente password.

**Endpoint**: `POST /docente/api/actualizar-contrasena/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
contrasena_actual: string (required)
nueva_contrasena: string (required)
confirmar_contrasena: string (required)
```

**Response**:
```json
{
  "success": true,
  "message": "Contraseña actualizada exitosamente"
}
```

**Error Responses**:
- `400`: Current password incorrect, passwords don't match

**Status Codes**: 200, 400

---

### POST /docente/api/actualizar-progreso/

Update docente progress.

**Endpoint**: `POST /docente/api/actualizar-progreso/`

**Authentication**: Required (Docente role)

**Request Body** (form-data):
```
progreso_id: integer (required)
estado: string (required)
comentarios: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Progreso actualizado exitosamente"
}
```

**Status Codes**: 200, 400, 404

---

## Generador Role Endpoints

### POST /generador/api/crear-curso-generador/

Create a course from generator panel.

**Endpoint**: `POST /generador/api/crear-curso-generador/`

**Authentication**: Required (Generador role)

**Request Body** (form-data):
```
titulo: string (required)
descripcion: string (optional)
nivel: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Curso creado exitosamente",
  "curso_id": 1
}
```

**Status Codes**: 200, 400, 403

---

### POST /generador/api/actualizar-curso-generador/<int:curso_id>/

Update a course from generator panel.

**Endpoint**: `POST /generador/api/actualizar-curso-generador/<curso_id>/`

**Authentication**: Required (Generador role)

**Request Body** (form-data):
```
titulo: string (optional)
descripcion: string (optional)
estado: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Curso actualizado exitosamente"
}
```

**Status Codes**: 200, 400, 403, 404

---

### POST /generador/api/eliminar-curso-generador/<int:curso_id>/

Delete a course from generator panel.

**Endpoint**: `POST /generador/api/eliminar-curso-generador/<curso_id>/`

**Authentication**: Required (Generador role)

**Response**:
```json
{
  "success": true,
  "message": "Curso eliminado exitosamente"
}
```

**Status Codes**: 200, 400, 403, 404

---

### POST /generador/api/guardar-curso-generado/

Save an AI-generated course.

**Endpoint**: `POST /generador/api/guardar-curso-generado/`

**Authentication**: Required (Generador role)

**Request Body** (JSON):
```json
{
  "titulo": "string (required)",
  "descripcion": "string (optional)",
  "contenido": {
    "modulos": [],
    "estructura": {}
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Curso generado guardado exitosamente",
  "curso_id": 1
}
```

**Status Codes**: 200, 400, 403

---

### GET /generador/api/obtener-estadisticas/

Get course statistics.

**Endpoint**: `GET /generador/api/obtener-estadisticas/`

**Authentication**: Required (Generador role)

**Response**:
```json
{
  "success": true,
  "data": {
    "total_cursos": 10,
    "cursos_aprobados": 7,
    "cursos_pendientes": 2,
    "cursos_rechazados": 1
  }
}
```

**Status Codes**: 200

---

### POST /generador/api/actualizar-perfil-generador/

Update generator profile.

**Endpoint**: `POST /generador/api/actualizar-perfil-generador/`

**Authentication**: Required (Generador role)

**Request Body** (form-data):
```
nombre: string (optional)
apellido_paterno: string (optional)
apellido_materno: string (optional)
correo: string (optional)
```

**Response**:
```json
{
  "success": true,
  "message": "Perfil actualizado exitosamente"
}
```

**Status Codes**: 200, 400

---

## AJAX Endpoints

### POST /agente-ajax/

Agent AJAX endpoint for role-based data.

**Endpoint**: `POST /agente-ajax/`

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {}
}
```

**Status Codes**: 200

---

### POST /docente/ajax/

Docente AJAX endpoint for dynamic data.

**Endpoint**: `POST /docente/ajax/`

**Authentication**: Required (Docente role)

**Response**:
```json
{
  "success": true,
  "data": {}
}
```

**Status Codes**: 200

---

### POST /evaluador/ajax/

Evaluator AJAX endpoint for dynamic data.

**Endpoint**: `POST /evaluador/ajax/`

**Authentication**: Required (Evaluador role)

**Response**:
```json
{
  "success": true,
  "data": {}
}
```

**Status Codes**: 200

---

### POST /generador/ajax/

Generator AJAX endpoint for dynamic data.

**Endpoint**: `POST /generador/ajax/`

**Authentication**: Required (Generador role)

**Response**:
```json
{
  "success": true,
  "data": {}
}
```

**Status Codes**: 200

---

## Rate Limiting

Some endpoints implement rate limiting to prevent abuse:

- User creation/update: 10 requests per hour per IP
- Rate limit key format: `rate_limit:{endpoint_name}:{ip}`

When rate limit is exceeded, the API returns:
```json
{
  "success": false,
  "error": "Demasiados intentos. Intente más tarde."
}
```

Status code: 429

---

## Error Handling

All endpoints implement comprehensive error handling with appropriate logging:

- **Security events**: Logged to `logs/security.log`
- **Application errors**: Logged to `logs/error.log`
- **Rate limit violations**: Logged to security logger

---

## CORS Configuration

The system allows cross-origin requests from configured origins. Configure in environment variables:

```env
CORS_ALLOW_ORIGINS='["*"]'
CORS_ALLOW_CREDENTIALS="true"
CORS_ALLOW_METHODS='["*"]'
CORS_ALLOW_HEADERS='["*"]'
```

---

## API Versioning

Current API version: 1.0.0

Version information is included in health check responses.

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8001/health/

# Get courses (requires authentication cookie)
curl -b cookies.txt http://localhost:8001/api/cursos/listar/

# Create user (admin only)
curl -X POST -b cookies.txt \
  -F "nombre=Juan" \
  -F "apellido_paterno=Pérez" \
  -F "correo=juan@example.com" \
  -F "contrasena=password123" \
  -F "curp=PERJ800101HDFXXX01" \
  -F "rol=1" \
  -F "institucion=1" \
  http://localhost:8001/api/usuarios/agregar/
```

### Using Python requests

```python
import requests

# Health check
response = requests.get('http://localhost:8001/health/')
print(response.json())

# Get courses
response = requests.get('http://localhost:8001/api/cursos/listar/', cookies=session)
print(response.json())
```

---

## WebSocket Support

Currently, the system does not implement WebSocket endpoints. All communication is via HTTP/HTTPS.

---

## Future API Enhancements

Planned improvements:
- Add pagination to list endpoints
- Implement OAuth2/JWT authentication
- Add OpenAPI/Swagger documentation
- Implement API versioning in URL paths
- Add request/response validation schemas
