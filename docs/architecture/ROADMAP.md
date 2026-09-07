---

### `docs/architecture/ROADMAP.md`

```markdown
# Roadmap de Evolución Arquitectónica
Este cronograma alinea las refactorizaciones técnicas con el valor entregado a las operaciones de la USICAMM.

## Fase 0: Contención y Estandarización (Actual - Q2)
* **Objetivo:** Estabilizar lo existente y cerrar puertas a código de baja calidad.
* **Hitos:**
  - [x] Implementación de pre-commits (`black`, `ruff`, `bandit`).
  - [x] Corrección de bugs de roles en núcleo Django (Normalización de `permisos.py`).
  - [ ] Implementación de `SECURITY_POLICY.md` (Eliminar *hardcoding* de credenciales en `docker-compose.yml`).

## Fase 1: Desacoplamiento e Identidad Unificada (Q3)
* **Objetivo:** Cumplir con la Arquitectura V1. Evitar que Django actúe como un proxy bloqueante.
* **Hitos:**
  - [ ] Implementación de autenticación JWT (JSON Web Tokens) en Django.
  - [ ] Refactorización de `agent_ajax.py`. El frontend consumirá `ia_service_core` directamente enviando el Bearer Token.
  - [ ] Separación Lógica de Base de Datos: Crear `schema_ai` y `schema_reports` en el servidor PostgreSQL actual.

## Fase 2: Automatización Asíncrona Orientada a Eventos (Q4)
* **Objetivo:** Cumplir con la Arquitectura V2. Preparar el sistema para dictaminar a miles de docentes simultáneamente.
* **Hitos:**
  - [ ] Despliegue de un Message Broker central (Migrar de Redis a RabbitMQ para mayor resiliencia de eventos).
  - [ ] Convertir la ingesta de documentos RAG a un proceso asíncrono (Event-driven) en `ms_validation`.
  - [ ] Despliegue de infraestructura de Observabilidad (Prometheus + Grafana) para monitorear el rendimiento de los Workers y de Ollama.