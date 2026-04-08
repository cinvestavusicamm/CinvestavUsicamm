# Estado Actual de la Arquitectura (As-Is)
**Fecha:** Abril 2026 | **Fase:** Híbrida Temprana

## Diagrama C4: Contenedores
Actualmente, el monolito de Django centraliza tanto la UI como la lógica principal. Los microservicios de IA (`backend_api`, `ia_service_core`, `ms_reports`) operan de manera satelital, generando fragmentación en los flujos de RAG y duplicidad de adaptadores.

```mermaid
graph TD
    User((Usuario / USICAMM))
    
    subgraph Ecosistema EscalafonIA
        UI[Django Monolith UI\napps/views]
        Core[Django Core\nModelos/Permisos]
        DB[(PostgreSQL Central)]
        
        MSR[ms_reports\nFastAPI/Celery]
        MSV[ms_validation\nFastAPI]
        IA_Core[ia_service_core\nRAG Orquestador]
        IA_Back[backend_api\nFragmento RAG]
        
        Qdrant[(Qdrant Vector DB)]
        Redis[(Redis Cache/Broker)]
    end
    
    Ollama[Ollama LLM Externo]

    User --> UI
    UI --> Core
    Core --> DB
    
    Core -->|HTTP Sync| MSR
    Core -->|HTTP Sync| MSV
    Core -->|HTTP Sync| IA_Core
    
    MSR --> Redis
    MSR --> Qdrant
    IA_Core --> Qdrant
    IA_Back --> Qdrant
    
    IA_Core --> Ollama
    MSR --> Ollama
    
    style DB fill:#3366cc,color:#fff
    style Qdrant fill:#ff9900,color:#fff