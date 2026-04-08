# Estado Actual de la Arquitectura (As-Is)
**Fecha:** 08 Abril 2026 | **Fase:** Monolito Distribuido

## Resumen del Diagnóstico
El ecosistema actual opera bajo un anti-patrón conocido como **"Monolito Distribuido"**. Aunque existen múltiples repositorios y servicios (Django, `ia_service_core`, `ms_reports`), están fuertemente acoplados por dos puntos críticos:
1. **Shared Database:** Todos los servicios leen/escriben en la misma base de datos PostgreSQL (`dev_db`).
2. **Integración Síncrona Bloqueante:** Django actúa como proxy inverso, deteniendo sus propios hilos (hasta por 180s) esperando la respuesta de la IA.

## Diagrama C4 (Nivel Contenedores)

```mermaid
flowchart TD
    %% Actores
    User((Usuario\nDocente/Evaluador))

    %% Monolito
    subgraph Monolith [Núcleo Django - Monolito]
        Auth[Módulo Sesiones]
        Ajax[Vistas Ajax Proxy]
    end

    %% Microservicios
    subgraph Microservices [Microservicios AI / Workers]
        IA[ia_service_core\nFastAPI]
        Validation[ms_validation\nFastAPI]
        Reports[ms_reports\nCelery/FastAPI]
        Common[[ia_common\nLibrería Compartida]]
    end

    %% Infraestructura
    subgraph Infra [Infraestructura de Datos Compartida]
        DB[(PostgreSQL\nShared DB)]
        Vector[(Qdrant\nBase Vectorial)]
        Redis[(Redis\nBroker/Cache)]
    end

    %% Conexiones
    User -->|HTTP (Cookies)| Auth
    User -->|AJAX| Ajax
    Ajax -->|HTTP Síncrono (Sin Auth Real)| IA
    
    Auth -->|Lee/Escribe| DB
    IA -->|Lee/Escribe (SQLAlchemy)| DB
    Reports -->|Lee/Escribe| DB
    
    IA -->|Búsqueda RAG| Vector
    Validation -->|Búsqueda| Vector
    Reports -->|Búsqueda Manuales| Vector
    
    Common -.-> IA
    Common -.-> Validation
    
    style DB fill:#ffcccb,stroke:#ff0000,stroke-width:2px
    style Ajax fill:#ffcccb,stroke:#ff0000,stroke-width:2px