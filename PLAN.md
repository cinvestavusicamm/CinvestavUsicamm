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

### DEUDA-4. Rutas rotas en producción que el smoke test ocultaba

**Ambos fallos existían en producción** y no se detectaban. Ninguno era del smoke test:

| Ruta | Qué pasaba | Qué se hizo |
|---|---|---|
| `/docente/index/` | `index_docente` renderizaba `docente/index_docente.html`, que **no existe** en el repositorio. Cualquier DOCENTE que abriera la ruta recibía un **500 con `TemplateDoesNotExist`**. | La vista ahora redirige a `Docente:panel_docente`. El contexto que armaba era idéntico al del panel. |
| `/evaluador/chat/` | `chat` renderizaba `Evaluador/chat_ia.html`, que **no existe**. Cualquier EVALUADOR que abriera el chat recibía un **500**. | Ruta retirada del enrutado. La vista y su JS quedan sin tocar. |

**Cómo se ocultaban.** Los siete bucles de `test_views_smoke.py` envolvían la petición en
`try/except Exception`, y si algo fallaban imprimían un `✗` y continuaban. Los dos 500 se
contabilizaban como aprobado. El `try/except` se retiró en `4c45769` y los 25 fallos que
aparecieron estaban en la vista del smoke test, no en la aplicación: faltaba una barra inicial
en cuatro rutas AJAX y `_login_con_rol` fijaba `usuario_id = 1` en una base de test vacía.

**Verificación previa a tocar nada.** Ninguna plantilla, JS ni menú enlaza a
`Docente:index_docente`, `/docente/index/`, `evaluador:chat` ni `/evaluador/chat/`; las únicas
referencias estaban en dos tests. `panel_docente` no redirige a `index_docente`, así que el
redirect no introduce bucle.

### DEUDA-5. Chat del evaluador sin plantilla, pendiente

**Estado:** la ruta `evaluador:chat` se retiró del enrutado, pero **la vista sigue existiendo** en
`apps/users/views/evaluador/chat.py` y su JS también. Falta la plantilla `Evaluador/chat_ia.html`.

Para rehabilitar el chat hay que escribir esa plantilla. No es cuestión de descomentar una línea:
`templates/Evaluador/` tiene ocho plantillas y ninguna de chat, y no hay equivalente al que
adaptarla. Decidir si el chat vive en el microservicio de IA o dentro de Django es requisito
previo.

### DEUDA-7. Tres endpoints AJAX de rol sin consumidor y solo con chequeo de cookie

**Estado: protegidos por rol, pendientes de decidir si se retiran.**

`/docente/ajax/`, `/evaluador/ajax/` y `/generador/ajax/` solo miraban que la cookie tuviera
`usuario_id`, sin comprobar el rol, y eran `@csrf_exempt`. Cualquier usuario autenticado —de
cualquier rol— podía gastarse el microservicio de IA desde ellos.

Ahora llevan `@requiere_rol(ROLE_DOCENTE)`, `@requiere_rol(ROLE_EVALUADOR)` y
`@requiere_rol(ROLE_GENERADOR)` respectivamente, que releen el rol en la base.

**No hay consumidor.** Ningún JS ni plantilla hace POST a estas tres rutas exactas. Conviene
no confundirlas con vistas parecidas que sí están en uso y ya estaban protegidas:
`/generador/ajax/datos/` (la consume `static/js/generador/cursos.js`) apunta a
`generador_datos_ajax`, que es otra vista.

**Quedan abiertas dos decisiones**, ambas bloqueadas por lo mismo:

1. Si el chat de cada rol se rehabilita, estas vistas son su endpoint natural y la protección
   por rol que se acaba de poner es la correcta.
2. Si el chat vive en el microservicio y Django solo orquesta, estas vistas sobran y conviene
   borrarlas con sus tres plantillas muertas por el camino.

Hasta resolverlo, seguirlas hace que un usuario con el rol correcto reciba `302/401/403` en vez
de una respuesta inventada. Para decidir hay que trazar primero el flujo real de creación de
cursos con IA (ver "Tareas solicitadas fuera del plan original"), porque `docente_ajax` sí
invoca `ms_ai_agent_service` y no está claro si `generador_ajax` participa en ese camino o si
es otro resto igual que este.

---

### DEUDA-8. La clave de servicio entre Django y el microservicio de IA, en cuatro sitios y con tres nombres

**Estado: RESUELTO. Nombre canónico `INTERNAL_SERVICE_KEY`; Django y el microservicio lo leen.**

El valor compartido vive en cuatro ficheros, y no con el mismo nombre:

| Dónde | Cómo | Quién lo lee |
|---|---|---|
| `apps/users/api/agente.py` | **texto plano en el código** (ya no) → ahora `settings.INTERNAL_SERVICE_KEY` | Django, al mandar `X-Internal-Service-Key` |
| `ia_service_core/src/infrastructure/api/security.py:8` | `os.getenv("microAI", <valor escrito>)` | el microservicio, en `verify_internal_key` |
| `infrastructure/docker-compose.yml:69` | `MICROSERVICE_SECRET: <valor escrito>` (servicio `backend`) | **nadie** |
| `infrastructure/docker-compose.yml:111` | `MICROSERVICE_SECRET=<valor escrito>` (servicio `django`) | **nadie** |
| `ia_service_core/docker-compose.yml:22` | `MICROSERVICE_SECRET: ${MICROSERVICE_SECRET:-super_secreto_interno}` | **nadie** |

**El bug de fondo.** El microservicio busca `microAI`, que no pone nadie en ningún
`docker-compose.yml` ni en `.env.example`, así que siempre cae en el literal de
respaldo de `security.py`. Los `MICROSERVICE_SECRET` que sí se pasan no los lee
nadie. Funciona porque Django y el microservicio tienen **la misma cadena escrita a
mano dos veces**; el transporte de la variable nunca ha funcionado.

**Consecuencia del arreglo de Django.** `INTERNAL_SERVICE_KEY` ya es obligatoria y
sin valor por defecto. El día que alguien la defina en `.env` con un valor propio,
Django dejará de mandar el literal y el microservicio seguirá esperando el suyo:
`/ask` responderá 403 y el chatbot dirá "error inesperado". Es decir, **este arreglo
no se puede activar en un entorno real hasta unificar los nombres**.

**Arreglo mínimo pendiente de decisión:** leer `INTERNAL_SERVICE_KEY` en
`security.py` y quitarle el literal de respaldo, y borrar los `MICROSERVICE_SECRET`
muertos de los tres compose. Falta decidir si el nombre canónico es
`INTERNAL_SERVICE_KEY` (lo que ya usan Django y `.env.example`) o `microAI` (lo que
usa el microservicio), y eso depende de si hay otros consumidores fuera del repo.

**Lo que sí está hecho en este commit:** la credencial versionada desaparece de
`apps/users/api/agente.py`, `INTERNAL_SERVICE_KEY` está documentada en `.env.example`,
`core.settings.prov` se niega a arrancar sin ella, y `clave_del_servicio()` falla con
un mensaje que dice qué variable falta y dónde definirla.

**Arreglo aplicado (nombre canónico `INTERNAL_SERVICE_KEY`, decidido).**

| Fichero | Antes | Ahora |
|---|---|---|
| `ia_service_core/.../security.py` | `os.getenv("microAI", <valor escrito>)` | `os.getenv("INTERNAL_SERVICE_KEY", "")` + `RuntimeError` al importar si falta |
| `infrastructure/docker-compose.yml` | `MICROSERVICE_SECRET` en `backend` y `django`, leído por nadie | `INTERNAL_SERVICE_KEY: ${INTERNAL_SERVICE_KEY:?...}` en ambos |
| `ia_service_core/docker-compose.yml` | `MICROSERVICE_SECRET: ${...:-super_secreto_interno}` | `INTERNAL_SERVICE_KEY: ${INTERNAL_SERVICE_KEY:?...}` |
| `docker-compose.yml`, `docker-compose.prod.yml` | Django sin clave | `INTERNAL_SERVICE_KEY: ${INTERNAL_SERVICE_KEY:?...}` en `django` |

`microAI` desaparece: nadie la definía, así que solo servía para activar el literal
de respaldo. Los `MICROSERVICE_SECRET` también: nadie los leía. Y `${VAR:?}` hace que
`docker compose up` se niegue a arrancar, en vez de dejar el microservicio sin clave
(que ahora se niega a importar) o dejar `/agente-ajax/` devolviendo 500.

Comprobado: los cuatro compose cortan el arranque sin la variable y renderizan con
ella; `security.py` lanza `RuntimeError` sin ella (e ignora `microAI`), lee la
variable correcta con ella, y da 403 ante clave vacía, ausente o distinta.

**Pendiente para quien despliegue:** generar una clave **nueva**
(`python -c "import secrets; print(secrets.token_urlsafe(48))"`). La anterior está
escrita en texto plano en `security.py` y en dos compose, así que sigue en el
historial de git (`git log -p -S microAI`). Ya no sirve para nada, pero hay que dar
por caducado todo entorno que la usara.

**Ajeno a este arreglo, menor:** `ia_service_core/docker-compose.yml` es un fragmento
que ya estaba roto antes de tocarlo (`depends_on: database`, un servicio que no
define). El stack que funciona es `infrastructure/docker-compose.yml`.

---

### DEUDA-9. El estado de un curso se escribia desde once sitios y se leia contra tres listas

**Estado: RESUELTO. Una sola lista en `apps/users/config/constants.py`, `choices` en el modelo, y una función que normaliza las variantes.**

Lo que había:

| Dónde | Qué usaba |
|---|---|
| `plantillas/generador_cursos/generador_de_cursos.html` | guardaba **`EnRevision`** (sin guion ni tilde) |
| `views/evaluador/validaciones.py` | `Aprobado`, `Rechazado`, `En_Revisión` |
| `views/docentes/consultar_progreso.py` | comparaba con `Aprobado`, **`Publicado`**, **`En Progreso`** |
| `views/generador_cursos/estadisticas_cursos.py` | contaba **`Activo`** y **`Completado`** |
| `plantillas/docente/vertical.html` | `Aprobado`, **`Publicado`**, **`En Progreso`** |
| `plantillas/generador_cursos/mis_cursos.html` | `Aprobado`, **`En Revisión`** (con espacio), **`Observaciones`** |
| `plantillas/generador_cursos/index_generador_de_cursos.html` | `Aprobado`, **`En Revisión`**, **`Observaciones`** |
| `static/js/generador/cursos.js` | mapa de clases con `Borrador`, `Aprobado`, `Rechazado`, `En_Revisión`, **`Publicado`** (y sin `Inactivo`) |
| `validators/__init__.py` | lista propia: `Borrador`, **`Pendiente`**, **`Revisión`**, `Aprobado`, `Rechazado`, `Inactivo`. **No la llamaba nadie** |

El daño era silencioso. Un curso enviado a revisión desde la interfaz quedaba
como `EnRevision`, y ninguna comparación por igualdad contra el `En_Revisión` del
evaluador lo encontraba. Los tableros no se enteraban porque cuentan con
`icontains("revision")`, que absorbe las dos escrituras. Las ramas que
comparaban `Publicado`, `En Progreso`, `Activo`, `Completado` y `Observaciones`
no se ejecutaban nunca, porque nadie escribía esos valores: dos contadores de
estadísticas daban 0 siempre y el 50 % de progreso de `consultar_progreso` era
inalcanzable.

**Arreglo aplicado.**

- `ESTADOS_CURSO`, `ESTADO_BORRADOR`…`ESTADO_INACTIVO` y `ESTADOS_CURSO_CHOICES`
  en `apps/users/config/constants.py`, junto a los roles.
- `reconocer_estado_curso()` reduce el valor a una clave comparable (sin
  tildes, espacios, guiones ni mayúsculas) y devuelve el estado canónico o
  `None`. `normalizar_estado_curso()` encima, con defecto `Borrador`. Dos
  funciones y no una porque quien llama tiene que poder distinguir "no me
  pasaron estado" (un borrador) de "me pasaron uno que no conozco" (un 400).
- Variantes que ya pueden estar guardadas y su destino: `EnRevision`,
  `En Revisión`, `Revisión`, `Pendiente` → `En_Revisión`; `Publicado`,
  `Completado` → `Aprobado`; `Observaciones` → `Rechazado`.
- `choices` en `Curso.estado`. Migración `0008_curso_estado_choices`, un solo
  `AlterField`: `sqlmigrate` sale como `-- (no-op)` porque `choices` no se
  aplica en la base. Comprobado aplicando la migración sobre una base con
  cursos en `EnRevision`, `En Revisión`, `Publicado`, `En Progreso`,
  `Observaciones` y `Borrador`: las filas salen igual, con su `contenido_json`,
  su `generado_con_ia` y su `fecha_creacion` intactos.
- `CursoValidator.validar_estado` delega en la constante única. Sigue sin
  llamarse desde ninguna parte.
- Escrituras y lecturas corregidas: la plantilla del generador manda
  `En_Revisión`; `consultar_progreso` y `estadisticas_cursos` usan las
  constantes; `vertical.html`, `mis_cursos.html` e
  `index_generador_de_cursos.html` comparan estados canónicos; `cursos.js`
  mapea `Inactivo` en vez de `Publicado`.
- `test_curso_service.py` ya no fija `Publicado`.

**Lo que NO se tocó, a propósito.** Los lectores con `icontains`
(`repositories/__init__.py`, `evaluador/reportes.py`, `router_service.py`,
`dashboard_builders.py`, `js/evaluador/reportes.js`) se quedan como estaban: son
los que hacen que los cursos guardados antes de este arreglo sigan contando en
los tableros. Pasarlos a igualdad exacta exigiría antes una migración de datos
que normalice las filas existentes, y eso no se ha hecho. La función está lista
para cuando se decida.

**Pendiente, y no de este arreglo:** `makemigrations` sigue proponiendo 21
operaciones de deriva acumulada en otros modelos (`retroalimentacioniacurso`
sobre todo: renombrar `fecha`→`fecha_generacion`, `id`→`id_retroalimentacion`,
`comentario`→`sugerencias`, quitarle la FK `curso`, y renombrar la tabla). Eso
es anterior a este trabajo y va por separado. La migración 0008 está escrita a
mano para no mezclarse con eso.

### DEUDA-10. Tres endpoints de creación de cursos para GENERADOR, uno sin autenticación

**Estado: RESUELTO. Las tres superficies duplicadas se retiraron; queda
`/generador/api/crear-curso-generador/`.**

Había tres vistas distintas para crear un curso, y la que se pidió confirmar con
grep resultó no ser la única sin consumidor:

| Ruta | Vista | Decoradores | Estado |
|---|---|---|---|
| `/generador/api/crear-curso-generador/` | `views/generador_cursos/cursos.py` | `csrf_exempt` + rol | rota (CSRF apagado) |
| `/generador/api/crear/` | `api/cursos.py` | `csrf_exempt` + rol | rota |
| `/api/cursos/crear/` | `api/cursos_api.py` → `api/cursos.py` | `csrf_exempt` + rol | rota |
| `/generador/api/crear-curso-index/` | `views/generador_cursos/index_generador.py` | `csrf_exempt` + rol | rota |
| `views/generador_cursos/crear_curso_api.py` | copiada de `api/cursos.py` | `csrf_exempt` + rol | ni registrada |

Las cuatro rotas usan `docente_id=request.user.id`. El login de este proyecto es
por sesión propia, no de `django.contrib.auth`, así que `request.user` es un
`AnonymousUser` y `.id` no existe: no podían crear nada.

**El hallazgo que cambia el tono de esta deuda es otro.** Al revisar el grep
pedido, la única que de verdad respondía sin autenticación era
`GET /api/cursos/listar/`, en `api/cursos_api.py`: no lleva `requiere_rol` y
devolvía `Curso.objects.all().values()`. Comprobado contra una fila real de
prueba, sin sesión y sin token:

```
GET /api/cursos/listar/  ->  200
{"success": true, "data": [{"id_curso": 1, "titulo": "Curso privado",
  "descripcion": "secreto", "docente_id": 1, "estado": "Borrador",
  "generado_con_ia": false, "contenido_json": {"perg": "respuestaSecreta"}}],
  "count": 1}
```

Es decir: todos los cursos del sistema y su `contenido_json`, a cualquiera que
preguntara. Con `@csrf_exempt` encima. En el despliegue con nginx `/api/` lo
manda al gateway, que reescribe a `/api/v1/...` y no alcanza estas rutas; pero
`docs/API.md` las documentaba contra `localhost:8001` en directo, así que en
desarrollo y en cualquier acceso directo a Django estaba expuesta.

**Por qué se borra la superficie en vez de arreglarla.** Sin consumidor no hay
nada que proteger: nadie la llama y no se pierde ninguna capacidad, porque las
mismas operaciones siguen en las rutas del panel que sí consume la interfaz. Es
el mismo criterio del commit `0671d40`, que retiró `/api/usuarios/*`.

**Consumer check (el grep que se pidió, con alcance de todo el repositorio).**
Cero llamadas en `templates/` y `static/`. Fuera de ahí, la única referencia
viva era `ms_orchestrator`, en `DjangoBackendClient`: `get_cursos`,
`create_curso` y `update_curso` apuntan a estas rutas, pero **nadie los invoca**
dentro de `ms_orchestrator` (0 llamadas). Además ese cliente no manda cookie ni
cabecera de autenticación, y las vistas se autenticaban por sesión, así que
aunque se invocasen no habrían funcionado. Sus tres métodos se conservan
marcados `SIN USO` con el motivo, igual que se hizo con los de usuarios.

**Arreglo aplicado.**

- Borrados `apps/users/api/cursos.py`, `apps/users/api/cursos_api.py` y
  `apps/users/views/generador_cursos/crear_curso_api.py` (esta última no estaba
  registrada en ninguna parte: nadie la importaba).
- Fuera sus rutas de `urls.py` y `routes/generador_urls.py`.
- De la vista que queda se quitó `@csrf_exempt` y se invirtieron los
  decoradores, para que `@requiere_rol(ROLE_GENERADOR)` se evalúe antes de
  `@require_http_methods`. Ahora un usuario sin rol recibe 403 también si usa
  GET, en vez de un 405 que no explica nada.
- `generador_de_cursos.html` emite `{% csrf_token %}`. Estaba el `X-CSRFToken`
  en el JS, pero el token solo lo imprimían login y registro: si el usuario
  entraba por otro lado, la cabecera llegaba vacía. Con el `csrf_exempt` fuera,
  eso rompía la creación, así que la plantilla tiene que emitirlo siempre.
- El contenido se valida **antes** de crear la fila. Se validaba después, con
  lo que un contenido de más de 1 MB dejaba el curso creado y un 400 en la cara
  del usuario. Ahora el 400 significa que no se creó nada.
- `test_crear_curso_endpoint.py` (23 tests) y `test_agente_timeouts.py`
  (15 tests) cubren la cadena de decoradores completa a traves del cliente de
  Django, no llamando a la vista directamente.

**Lo que NO se tocó, a propósito.**

- `crear_curso_index` en `index_generador.py` sigue registrada en su propia
  ruta y con sus mismos problemas. No esCreation del panel del generador de IA,
  es la creación del curso semilla del panel, y mezclarla aquí sería otro
  arreglo distinto. Anotado abajo.
- `ms_ai_agent_service`, que tampoco se extiende.

### DEUDA-11. `crear_curso_index`: el mismo endpoint de creación, otra vez

**Estado: ABIERTO. No es lo mismo que lo que se acaba de arreglar, y conviene
no confundirlos.**

`/generador/api/crear-curso-index/` (`views/generador_cursos/index_generador.py`)
tiene los dos primeros problemas: `@csrf_exempt` y el orden de decoradores
invertido. Pero no el tercero: lee `request.session.get('usuario_id')`, asi que
esta sí crea cursos. El `str(e)` en el `except` también devuelve la excepción
cruda al cliente.

No se toca en el mismo commit por dos razones. La primera es que tampoco tiene
consumidor (0 referencias a `crear-curso-index` en `templates/` y `static/`),
igual que las que se acabaron de retirar. La segunda es que su flujo es otro:
crea el curso semilla que abre el panel, no un curso por petición de la
interfaz de generación, y decidir si debe evitarse duplicarlo cuando el panel ya
está abierto es una pregunta de producto que no está resuelta. Retirarlo sin
decidir eso podría quitar la forma de crear el curso inicial del panel.

### DEUDA-12. `ia_service_core` devuelve los fallos de la IA como 200 con el error dentro de `response`

**Estado: ABIERTO. Parcheado en Django; la correccion real es en el servicio.**

Verificado contra el servicio real (`POST /api/ask` con clave y sin Ollama
levantado): contesta `200` con
`{"response": "Error: No pude procesar tu pregunta (Fallo en Embedding)."}`.
El fallo de Ollama hace lo mismo con otro prefijo
(`"Error generando respuesta: ..."`) porque el adaptador
(`ia_service_core/src/infrastructure/external/ollama.py`) captura la excepcion y
devuelve una cadena en vez de propagarla, y `ChatRAGUseCase.run` hace lo propio.

Es decir: para el servicio, un fallo de la IA no es un error HTTP; es una
respuesta correcta cuyo texto empieza por "Error". Cualquier consumidor que solo
mire el estado pinta ese texto como si fuera la respuesta del modelo.

Mientras eso siga asi, `apps/users/api/agente.py` reconoce los dos prefijos
conocidos en `_SENTINELAS_FALLO_IA` y los traduce a `502`. Es un parche atado a
las cadenas exactas del servicio: si `ia_service_core` cambia el texto, el
usuario vuelve a ver el error como respuesta. La correccion de raiz es que el
adaptador de Ollama lance y que el router devuelva `502`/`503`, en vez de meter
el fallo en `response`. Se hace en el punto 5, junto con el endpoint de
generacion, que tambien necesita distinguir "JSON invalido" de "la IA fallo".

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

**Decisión del cliente (2026-10-04, Fase 0): no se tocan.** Se conservan las cuatro rutas, el módulo
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

**RESUELTO (2026-10-04, punto C).** El cliente revirtió la decisión de no tocar nada y se aplicó la
alternativa recomendada, por las razones ya verificadas: cero llamadas a los cuatro métodos en todo
el repositorio, `nginx` manda `/api/` al gateway y el gateway no tiene `usuarios` en su
`SERVICE_MAP`, y el orquestador no habría podido alcanzar las rutas ni por la barra final ni por
el formato del cuerpo.

Qué se eliminó: el módulo `apps/users/api/usuarios_api.py`, sus cuatro rutas en
`apps/users/urls.py`, la sección *User Management API* de `docs/API.md` y el ejemplo de `curl` que
usaba la ruta. Los cuatro métodos de `DjangoBackendClient` se conservan **marcados como SIN USO**,
con el motivo y las dos razones por las que nunca pudieron funcionar.

**Lo que NO se pierde.** Las operaciones de usuario siguen disponibles por sus rutas AJAX reales en
`apps/users/routes/administrador_urls.py`, que son las que consume el JS del panel:
`agregar_usuario_ajax`, `usuario/<id>/obtener/`, `usuario/<id>/editar/` y `toggle-usuario/<id>/`.
Las cuatro exigían sesión ADMIN, así que no se pierde ninguna capacidad.

**Pendiente que queda abierto:** el consumidor server-to-server declarado en el otro proyecto, si
alguna vez existe, pierde su ruta. Si aparece, hay que rehacer el contrato con API key según los
siete puntos de arriba, no resucitar estas rutas.

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

> **Avance parcial en Fase 1.** `toggle-admin.js` hablaba un formato que su vista nunca
> devolvía: leía `data.success` / `data.error` / `data.activo`, pero `toggle_usuario` responde con
> `respuesta_ok` (`estado` / `mensaje` / `datos`). El botón no actualizaba nada y pintaba un
> `alert(undefined)`. Se corrigió **solo** `toggle-admin.js` para hablar el formato real, porque
> Fase 1 exige que el rechazo se vea en pantalla. La unificación de los cuatro endpoints sigue
> pendiente: `editar_usuario_ajax` y `obtener_usuario_ajax` continúan con `JsonResponse` plano.

### DEUDA-6. `select_for_update` sin verificar: SQLite no lo ejecuta

**Regla aplicada en Fase 1:** un ADMIN no puede desactivarse ni cambiarse su propio rol, y el
sistema no puede quedar sin ningún ADMIN activo. Las reglas viven en `UserService`, no en el JS, y
aplican a editar y a toggle.

**Lo que está verificado** (SQLite, 117 tests): la lógica, el rollback y la auditoría del rechazo.
`test_admin_protection.py` cubre autodesactivación, cambio de rol propio, último ADMIN
desactivado, último ADMIN degradado, los dos casos permitidos con dos ADMIN, y que el rechazo queda
en bitácora con su código.

**Lo que NO está verificado: el bloqueo.** `select_for_update` requiere que el backend declare la
característica; el de SQLite no la declara y Django **lo ignora en silencio**, sin error ni aviso.
Los tests pasan igual, lo que hace fácil creer que la protección de concurrencia está ahí cuando en
esa base no hay nada. Solo en PostgreSQL hay `SELECT ... FOR UPDATE`.

**Cómo verificarlo, en local:**

```bash
# 1. Levantar solo PostgreSQL (pgvector/pgvector:pg16, puerto 5432)
docker compose up -d postgres

# 2. Esperar a que acepte conexiones
docker compose exec postgres pg_isready -U user -d cinvestav_db

# 3. Correr SOLO el test de concurrencia contra PostgreSQL
DJANGO_SETTINGS_MODULE=core.settings.dev \
DATABASE_URL=postgresql://user:password@localhost:5432/cinvestav_db \
./venv/bin/python manage.py test \
  apps.users.tests.test_admin_protection_concurrency --keepdb
```

El módulo se salta entero si la base no es PostgreSQL, así que en la suite normal aparece como
`skipped=1` y no da falsa confianza en ningún sentido.

**Qué demuestra y qué no.** El test lanza dos hilos, cada uno con su propia conexión, que intentan
apagar al ADMIN contrario tras pasar una barrera. Al terminar exige que quede **exactamente un**
ADMIN activo y que uno de los dos hilos fuera **rechazado**. Sin `select_for_update` los dos leerían
"hay dos" y los dos confirmarían, dejando cero. Una ejecución en verde no es prueba de que no haya
carrera: la barrera maximize la solapación pero no la garantiza. Lo que demuestra es que el segundo
hilo **rechaza** en lugar de dejar el sistema sin ADMIN, y conviene repetirlo varias veces.

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