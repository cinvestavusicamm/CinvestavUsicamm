---

### 📄 `docs/architecture/02_target_v1_modular.md`

```markdown
# Arquitectura Objetivo V1 (Transición Modular)
**Objetivo:** Seguridad, Desacoplamiento de Datos y Tolerancia a Fallos.

## Decisiones Arquitectónicas (ADR) Implementadas en V1
1. **Migración a JWT:** Django ya no usará sesiones basadas en cookies para hablar con los microservicios. Emitirá un JSON Web Token (JWT) que el frontend enviará directamente a las APIs.
2. **Database per Service (Lógico):** Se crearán esquemas separados en PostgreSQL (ej. `schema_django`, `schema_reports`, `schema_ai`) para evitar bloqueos cruzados sin necesidad de pagar por servidores extra.
3. **API Gateway Interno (Nginx/Traefik):** El frontend dejará de pasar por `agent_ajax.py`. El Gateway enrutará `/api/ai/*` directo a FastAPI y `/api/core/*` a Django, reduciendo la carga del monolito.

## Diagrama C4 Objetivo (V1)

```mermaid
flowchart TD
    User((Cliente SPA/Frontend))

    Gateway{API Gateway\nEnrutador / SSL}

    subgraph Core [Gestión de Identidad]
        Django[Django Identity Provider]
        DB_Django[(PG: schema_core)]
    end

    subgraph AI_Domain [Dominio de Inteligencia Artificial]
        FastAPI[Microservicios Unificados IA]
        DB_AI[(PG: schema_ai)]
        Vector[(Qdrant)]
    end

    User -->|Petición + JWT| Gateway
    Gateway -->|/auth| Django
    Gateway -->|/api/ai + JWT| FastAPI
    
    Django -->|Verifica Credenciales| DB_Django
    Django -.->|Firma JWT| User
    
    FastAPI -->|Valida Firma JWT| DB_AI
    FastAPI --> Vector
    
    style Gateway fill:#d4edda,stroke:#28a745,stroke-width:2px

---

### 📄 `docs/architecture/03_target_v2_scalable.md`

```markdown
# Arquitectura Objetivo V2 (Escalabilidad Asíncrona)
**Objetivo:** Arquitectura Orientada a Eventos (EDA) para procesamiento masivo de la USICAMM.

## La Meta Final
El ecosistema dejará de depender de peticiones HTTP síncronas entre servicios. Cuando Django registre un nuevo docente o apruebe un curso, no llamará a un API; emitirá un evento a un **Message Broker** (RabbitMQ o Kafka). Los microservicios de IA o Reportes reaccionarán a estos eventos a su propio ritmo sin colapsar.

## Diagrama C4 Objetivo (V2)

```mermaid
flowchart TD
    User((Usuario USICAMM))

    Gateway{API Gateway}

    subgraph Event_Bus [Bus de Eventos Central]
        Broker[[RabbitMQ / Kafka]]
    end

    subgraph Core [Dominio Core]
        Django[Django Core]
        DB_Core[(DB Core)]
    end

    subgraph Reporting [Dominio Reportes]
        CeleryRep[Workers Reportes]
        DB_Rep[(DB Reportes)]
    end

    subgraph Evaluation [Dominio Evaluación IA]
        FastAPI[IA Service]
        Vector[(Vector DB)]
    end

    User -->|HTTP/WSS| Gateway
    Gateway --> Django
    Gateway -->|WebSocket| FastAPI
    
    Django -->|Emite: CursoAprobado| Broker
    Broker -->|Consume: GenerarPDF| CeleryRep
    Broker -->|Consume: ActualizarRAG| FastAPI
    
    CeleryRep --> DB_Rep
    FastAPI --> Vector
    
    style Broker fill:#cce5ff,stroke:#004085,stroke-width:2px