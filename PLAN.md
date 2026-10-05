# Plan de Finalización - EscalafonIA Jaguar

## Decisiones tomadas por el cliente (2026-10-04)
- Base de datos: **Postgres local en Docker. NO usar Supabase.**
- `DEBUG=False` como default; dev lo activa por variable de entorno; prod nunca en True.
- Unificar `ia_service_core` de Python 3.10 a 3.12.

## Definición de "Terminado"
- Proyecto ejecutable desde cero con Docker Compose
- Tests completos pasando (o con justificación documentada de los que no)
- README actualizado con instalación, uso, variables de entorno, scripts y versión de Python
- Configuración de settings coherente entre ambientes
- Sin secretos en archivos commiteados

## Tareas Priorizadas

### PRIORIDAD ALTA (Bloqueantes)
- [x] **0. Entorno de Python reproducible** (Hecho)
  - Dockerfile de Django usa `python:3.12-slim`; el resto 3.11/3.12; `ia_service_core` en 3.10 (pendiente unificar)
  - `venv/` recreado desde cero con **Python 3.12.15**, instalado solo desde `apps/requirements.txt`
  - `pip check`: sin dependencias rotas. Django 4.2, django-redis 5.4.0, celery 5.4.0
  - **Hallazgo**: el `AttributeError: 'super' object has no attribute 'dicts'` que se veía en Python 3.14 **desaparece en 3.12**. Era incompatibilidad de entorno, no bug de código
  - **Pendiente**: documentar Python 3.12 en README y añadir `.python-version`

- [x] **1. Seguridad de credenciales** (COMPLETADO - commits `6ee5bcf`, `995424b`)
  - `git ls-files .env`: NO trackeado. `git log --all -- .env`: nunca estuvo en el historial
  - **Sin historial que limpiar**: no hace falta `filter-repo`
  - `.gitignore` tenía marcadores de merge sin resolver → reglas de la rama `agente-prueba`
    nunca estuvo activas. Resuelto unificando ambos lados + `.env.*` con `!.env.example`
  - `ms_orchestrator/.env.local` estaba trackeado pese a que su `.gitignore` ya lo listaba.
    Quitado del índice con `git rm --cached` (sigue en disco)
  - **Acción del cliente recomendada**: rotar la contraseña de Supabase del `.env` local.
    No se commiteó nunca, pero lleva en texto plano desde el 31-Jul

- [x] **2. Arreglar tests de roles con constantes** (COMPLETADO - commit `e100cf8`)
  - `test_e2e_flow.py` y `test_auth_permissions_users.py` afirman contra `'Administrador'`/`'Docente'`
  - Reemplazados por `ROLE_ADMIN` / `ROLE_DOCENTE` de `apps.users.config.constants`
  - `fake_user.nombre = "Docente"` se conservó: es nombre de persona, no rol

- [x] **3. Fuga del mock de timezone** (COMPLETADO - commit `0a10f8d`)
  - Parcheado el nombre local `apps.users.views.auth_views.timezone` en vez de `timezone.now` del
    módulo global, para que el mock no se filtre a `django.contrib.sessions.backends.base`
  - `now()` ahora devuelve datetime naive, coherente con `USE_TZ=False`
  - Solo 1 test tenía el patrón; no hay otros que parcheen `timezone.now`

- [x] **5. Pin de Python** (COMPLETADO - commit `5ef5463`)
  - `.python-version` = `3.12` (sin parche)
  - Solo afecta al venv de Django, el único con `manage.py`

- [ ] **3. `USE_TZ`: DECIDIDO — NO aplicar el cambio** (Esfuerzo: Bajo)
  - El error `SQLite backend does not support timezone-aware datetimes` **NO es bug de producción**
  - Causa real: el test mockea `apps.users.views.auth_views.timezone.now`; como `django.utils.timezone`
    es un módulo singleton, el mock se filtra a `django.contrib.sessions.backends.base` y produce un
    datetime aware para `django_session.expire_date`
  - Prueba: en HEAD limpio, **quitando el mock del test el error desaparece**
  - Decisión: se descarta el cambio en `base.py`; se arregla el mock en el test (tarea 2)

- [x] **4. Eliminar `apps/users/infrastructure/decorators.py`** (COMPLETADO - commit `ab3cc21`)
  - Grep amplio confirmado: 0 referencias en codigo, templates, settings, docker-compose, scripts, docs
  - Sus 5 simbolos (`require_role`, `require_auth`, `validate_json`, `api_view`, `handle_exceptions`)
    no aparecen en ningun otro archivo; `__init__.py` del paquete esta vacio
  - El decorador real en uso es `requiere_rol` en `apps/users/services/permisos.py`
  - **Reportado aparte, NO borrado**: `exceptions.py` del mismo paquete, tambien con 0 importadores

### Hallazgos colaterales (sin tocar, requieren decision)
- [x] `.gitignore` con marcadores de conflicto de merge → RESUELTO (commit `6ee5bcf`)
- [x] `ms_orchestrator/.env.local` trackeado → RESUELTO (commit `995424b`)
- [ ] `apps/users/infrastructure/exceptions.py` — 0 importadores, igual que decorators.py
- [ ] Los 10 microservicios en `python:3.11-slim` — decidir si unificar a 3.12
- [ ] `test_integracion_flujo.py` y `test_microservice_integration.py` pasan por mocks,
      no verifican red real

## Deuda técnica registrada (2026-10-04, NO implementada)

### DEUDA-1. `apps/users/api/usuarios_api.py`: `@csrf_exempt` sobre vistas con sesión

**Corrección a una hipótesis previa:** estas vistas **sí exigen autenticación y rol**. No son
endpoints abiertos. Las cuatro funciones delegan en `obtener_usuario_ajax`,
`agregar_usuario_ajax`, `editar_usuario_ajax` y `toggle_usuario` de
`apps/users/api/usuarios.py`, y las cuatro llevan `@requiere_rol(ROLE_ADMIN)`. El decorador se
aplica aunque se invoquen desde otro envoltorio.

**Qué devuelve cada una, y sobre el hash de contraseña:**

| Endpoint | Devuelve | ¿Hash de contraseña? |
|---|---|---|
| `GET /api/usuarios/<id>/` | `success`, `id_usuario`, `nombre`, `apellido_paterno`, `apellido_materno`, `correo`, `curp`, `rol`, `institucion` | **No** |
| `POST /api/usuarios/agregar/` | `success`, `message`, `usuario_id` | **No** |
| `POST /api/usuarios/editar/<id>/` | `success`, `message` | **No** |
| `POST /api/usuarios/toggle/<id>/` | `estado`, `mensaje`, `datos{activo, contadores}` | **No** |

Ningún `SELECT` ni serializador de estas rutas expone `contrasena`. La contraseña solo se acepta
en entrada y se guarda con `make_password`. **No hay fuga de hash que corregir.**

**Quién las consume:** `ms_orchestrator/src/infrastructure/external/clients/service_clients.py`,
clase `DjangoBackendClient` (líneas 15-39). A su vez, ese cliente se instancia en la línea 214 del
mismo archivo. **Pero sus cuatro métodos no los invoca nadie**: 0 llamadas a `get_usuario`,
`create_usuario`, `update_usuario` y `toggle_usuario` fuera del propio cliente. Es código muerto.

**Verificado el 2026-10-04 (rama `vista-administrador`, Fase 0):** el atributo `self.django` solo se
usa para `health_check()` (línea 230) y `close()` (línea 242). Los cuatro métodos de usuarios no
tienen ninguna llamada en el repo.

**Consecuencia:** como exige sesión ADMIN, el orquestador no puede llamarlas en la práctica. Y si
lo intentara, fallaría por dos motivos independientes: pide `/api/usuarios/agregar` sin barra final
cuando la ruta es `/api/usuarios/agregar/`, y manda `json_data=` (cuerpo JSON) mientras la vista
lee `request.POST`.

Comprobado con `django.test.Client` y sesión ADMIN:

| Llamada tal y como la hace `DjangoBackendClient` | Respuesta |
|---|---|
| `POST /api/usuarios/agregar` (sin barra final) | `301` |
| `POST /api/usuarios/agregar/` con cuerpo JSON | `400` `Campos requeridos faltantes: …` |
| `POST /api/usuarios/agregar/` con `data=` form-encoded | `200` |

Las rutas **sí funcionan** por sí solas: `GET /api/usuarios/<id>/` devuelve `200` con el JSON
esperado. Lo que no existe es un consumidor capaz de alcanzarlas.

**Decisión del cliente (2026-10-04): no se tocan.** Se conservan las cuatro rutas, el módulo
`usuarios_api.py` y los métodos del orquestador. Motivo: hay un consumidor declarado en otro
proyecto, aunque esté muerto. La eliminación queda como decisión pendiente, no como deuda a aplicar
por omisión.

**Riesgo real que queda:** el `@csrf_exempt` es innecesario y peligroso. Un navegador con sesión
ADMIN abierta es vulnerable a CSRF contra estas rutas, porque el middleware está desactivado en
ellas aunque la autenticación por sesión siga activa. Como no hay consumidor real, el arreglo
natural es **borrar el módulo y sus cuatro rutas**, no autenticarlas.

**Arreglo propuesto (NO implementado), si se decide mantener el contrato server-to-server:**

1. Añadir `X-API-Key` obligatorio, con `hmac.compare_digest` contra un valor en el entorno.
   Se compara en tiempo constante y sin ramas que filtren por temporización.
2. Crear un decorador `requiere_api_key` en `apps/users/services/permisos.py`, junto a
   `requiere_rol`. No reutilizar `requiere_rol`: son esquemas distintos.
3. Las cuatro vistas pasan a exigir **API key en vez de** sesión ADMIN, no ambas cosas: son dos
  encia de autenticación incompatible para el mismo consumidor. Se evita el `or` que abriría la
   puerta a que un navegador con sesión ADMIN entre por la vía de la API key.
4. Un flag de entorno `ORCHESTRATOR_API_ENABLED`, apagado por defecto, para que activar el
   contrato sea deliberado.
5. Quitar `@csrf_exempt`: la autenticación por API key no necesita el token CSRF, y dejarlo
   además de estorba dejaría `@csrf_exempt` como un hueco por donde podría colarse un
   consumidor futuro con sesión.
6. Corregir el cliente del orquestador: barra final y `data=` en vez de `json_data=`, o mejor,
   que el cliente JSON y la vista lean `request.body` con `json.loads`.
7. Tests: sin API key → 401; con API key incorrecta → 401; con API key correcta → 200; y que un
   usuario con sesión ADMIN pero sin API key reciba 401, para fijar que son excluyentes entre sí.

**Alternativa más simple, que es la que se recomienda:** borrar `usuarios_api.py` y sus cuatro rutas
en `apps/users/urls.py`, más los métodos muertos de `DjangoBackendClient`. Se elimina la superficie
de ataque en vez de autenticarla. Decisión del cliente.

### DEUDA-2. Dos formatos de respuesta conviven en las vistas AJAX de admin

`apps/users/api/usuarios.py` mezcla dos convenciones:

| Convención | Dónde | Forma |
|---|---|---|
| `api_response.respuesta_ok` / `respuesta_error` | `agregar_usuario_ajax` (parcial), `editar_usuario_ajax` (parcial), `toggle_usuario` | `{"estado","mensaje","datos","errores"}` |
| `JsonResponse` plano | `obtener_usuario_ajax` | `{"success", ...campos sueltos}` |

Los errores también difieren: `respuesta_error` devuelve `estado: "error"`, mientras las rutas planas
devuelven `success: false` con `error`. Un cliente que normalice sobre `estado` se rompe contra
`obtener_usuario_ajax`, y al revés.

**Por qué no se unifica ya:** el JavaScript de `static/js/` está escrito contra la forma actual de
cada endpoint. Cambiarlo exige revisar y ajustar `agregarusuario-admin.js`,
`editarusuario-admin.js` y `toggle-admin.js` en el mismo cambio, con el riesgo de romper la
interfaz sin que los tests lo detecten (el backend no prueba el JS).

**Arreglo propuesto (NO implementado):** elegir `respuesta_ok` / `respuesta_error` como convención
única, porque es la que ya usa la mayoría de las vistas y la que maneja `errores` de forma
estructurada. Migrar `obtener_usuario_ajax` y las respuestas planas de las otras tres, y actualizar
el JS en la misma tarea. Conviene hacerlo junto con tests del lado del cliente o, en su defecto,
con una revisión manual del JS.

## Tareas solicitadas fuera del plan original (solo lectura, sin implementar)
- [ ] **Paso 1**: investigación de la vista de administrador
- [ ] **Paso 2**: investigación del flujo de creación de cursos con IA

### DEUDA-3. Deriva de migraciones (relevante para el Paso 2)

`makemigrations --check` sigue saliendo con código 3. Lo que queda, **sin corregir**:

| Qué | Detalle | Riesgo |
|---|---|---|
| `retroalimentacioniacurso` — nombre de tabla | El modelo declara `db_table = 'retroalimentacion_ia_curso'`; la migración `0003` creó `retroalimentaciones_ia_cursos` | La tabla del modelo **no existe** en ninguna base construida desde migraciones. Falla con `no such table: retroalimentacion_ia_curso` |
| `retroalimentacioniacurso` — campos | El autodetector quiere `RemoveField` de `id`, `curso`, `fecha`, `comentario` y `AddField` de `id_retroalimentacion`, `confianza_pbt`, `fecha_generacion`, `sugerencias`, `version` | Divergencia total entre modelo y migración. Igual que en la bitácora, el `RemoveField` de una PK destruiría datos: necesita `RenameField` |
| `bitacoraevento.usuario` | `AlterField` pendiente | Cosmético, la columna ya es `usuario_id` |
| `rol.nombre_rol`, `foro.descripcion` | `AlterField` pendientes | Cosméticos |
| 11 modelos con PK `id` | `colonia`, `cp`, `direccion`, `document`, `estado`, `municipio`, `procesoescalafon`, `prom`, `tipohogar` | `AutoField` → `BigAutoField`. En PostgreSQL es `serial` → `bigserial` |
| `Options` de `rol` y `retroalimentacioniacurso` | Faltan `ordering` y `verbose_name` | Cosmético |

**Consecuencia para el flujo de cursos con IA:** la retroalimentación de IA no tiene tabla. Cualquier
lectura o escritura de `RetroalimentacionIACurso` revienta. Conviene resolverlo antes de analizar el
flujo de creación de cursos, porque ese feedback es justamente lo que ese flujo produce.

**Nota sobre `0007`:** alalinea `bitacora_eventos` con su modelo, pero `makemigrations --check` seguirá
saliendo con error por lo demás. No se debe usar ese comando como criterio de "todo en orden"
mientras persista esta deriva.

- [ ] **5. Auditoría de microservicios** (Esfuerzo: Medio)
  - Tabla por servicio: endpoints reales vs esqueleto, quién lo consume, Dockerfile,
    presencia en docker-compose, tests
  - Proponer qué completar vs dejar fuera de alcance (el cliente decide)

- [ ] **6. `.env.example` completo** (Esfuerzo: Bajo)
  - Todas las variables usadas en settings + compose, con valores de ejemplo

### PRIORIDAD MEDIA
- [ ] **7. Unificar `ia_service_core` a Python 3.12** (Esfuerzo: Bajo) - aprobado por cliente
- [ ] **8. `docker compose up` limpio desde cero** (Esfuerzo: Medio)
- [ ] **9. Todos los tests pasando** (Esfuerzo: Medio)

### PRIORIDAD BAJA (Pulido)
- [ ] **10. Resolver marcadores de conflicto de merge en `.gitignore`** (Esfuerzo: Bajo)
- [ ] **11. Documentación**: README y `docs/` coherentes (Esfuerzo: Bajo)

## Log de ejecución

### Paso 0 — Entorno (COMPLETADO)
-instalado `python@3.12` vía Homebrew (3.12.15)
- `venv/` 3.14.3 (140M) eliminado y recreado en 3.12.15
- Instalación limpia desde `apps/requirements.txt`, sin versiones a mano
- `pip check`: `No broken requirements found`

**Resultados reales de los 57 tests:**

| Escenario | Resultado |
|---|---|
| HEAD limpio (Python 3.14 anterior) | `FAILED (failures=3, errors=1)` —incluía `AttributeError` de `copy(Context)` |
| HEAD limpio (Python 3.12) | `FAILED (failures=2, errors=1)` — el `AttributeError` desapareció |
| Con `USE_TZ=True` (Python 3.12) | `FAILED (failures=3)` — el error de tz desapareció,antasy que el fallo #3 |

**Desglose de los 3 fallos restantes (todos tests obsoletos, no código):**
1. `test_e2e_flow.py:50` — esperaba `'Administrador'`, la app devuelve `'ADMIN'` → CORREGIDO (commit `e100cf8`)
2. `test_e2e_flow.py:92` — esperaba `'Docente'`, la app devuelve `'DOCENTE'` → CORREGIDO (commit `e100cf8`)
3. `test_auth_permissions_users.py` — mock de `timezone.now` que se filtraba a Django → CORREGIDO (commit `0a10f8d`)

### Commits de testejos
| Commit | Qué hace |
|---|---|
| `e100cf8` | Tests de roles usan constantes en vez de strings fijos |
| `0a10f8d` | Aísla el mock de timezone para que no se filtre a Django |
| `5ef5463` | `.python-version` = 3.12 |

**Estado final de tests: `Ran 57 tests ... OK` (57/57)**
Verificado que no es falso positivo: 57 metodos `test_` declarados = 57 reportados, y con A y B
revertidos los tests vuelven a fallar (detecta las regresiones que corrigieron).

**Tests que hacen red real:** `test_integracion_flujo.py` y `test_microservice_integration.py` intentan
resolver `ms_ai_agent_service:8107` y loggedean `ConnectionError`, pero los assertions van sobre mocks,
así que pasan sin el servicio. Funcionalan dentro de Docker; fuera, documentar como limitación.

**Censo de Python por Dockerfile (16 Python):**
- 3.12 (5): raíz, `apps/` (Django), `backend_api`, `ms_orchestrator`, `ms_validation`
- 3.11 (10): ms_academic, ms_admin, ms_ai_agent, ms_api_gateway, ms_assessment, ms_auth, ms_course, ms_db, ms_notification, ms_reports
- 3.10 (1): `ia_service_core` — aprobado subir a 3.12, pendiente
- no-Python (2): `frontend_web`, `nginx` (nginx:alpine)
- **Pendiente de decisión del cliente**: si unificar los 10 de 3.11 a 3.12

**Tests que hacen red real (requieren servicios Docker):** `test_integracion_flujo.py`,
`test_microservice_integration.py` intentan resolver `ms_ai_agent_service:8107`. Fuera de alcance
en entorno local; a documentar.

## Criterios de Aceptación para "Terminado"
1. `docker compose up` levanta limpio desde cero
2. Los 57 tests pasan, o los que no pasan tienen justificación documentada
3. Sin secretos en archivos commiteados
4. Python 3.12 documentado en README y pinneado
5. Documentación coherente