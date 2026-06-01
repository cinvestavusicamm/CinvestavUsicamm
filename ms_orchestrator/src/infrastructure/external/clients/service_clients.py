"""Specific clients for each microservice in the system."""

import logging
from typing import Any, Dict, Optional

from ms_orchestrator.src.domain import ValidationRequest, AnalysisRequest
from .microservice_client import MicroserviceClient

logger = logging.getLogger(__name__)


class DjangoBackendClient(MicroserviceClient):
    """Client for the Django Backend (apps/)."""

    async def get_usuario(self, usuario_id: int) -> Dict[str, Any]:
        """Get usuario by ID."""
        logger.info(f"Calling DjangoBackend.get_usuario: {usuario_id}")
        return await self.get(f"/api/usuarios/{usuario_id}")

    async def create_usuario(self, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new usuario."""
        logger.info("Calling DjangoBackend.create_usuario")
        return await self.post(
            "/api/usuarios/agregar",
            json_data=usuario_data,
        )

    async def update_usuario(self, usuario_id: int, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing usuario."""
        logger.info(f"Calling DjangoBackend.update_usuario: {usuario_id}")
        return await self.post(
            f"/api/usuarios/editar/{usuario_id}",
            json_data=usuario_data,
        )

    async def toggle_usuario(self, usuario_id: int) -> Dict[str, Any]:
        """Toggle usuario active status."""
        logger.info(f"Calling DjangoBackend.toggle_usuario: {usuario_id}")
        return await self.post(f"/api/usuarios/toggle/{usuario_id}")

    async def get_cursos(self, docente_id: Optional[int] = None) -> Dict[str, Any]:
        """Get cursos, optionally filtered by docente."""
        logger.info(f"Calling DjangoBackend.get_cursos for docente: {docente_id}")
        params = {"docente_id": docente_id} if docente_id else {}
        return await self.get("/api/cursos/listar", params=params)

    async def create_curso(self, curso_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new curso."""
        logger.info("Calling DjangoBackend.create_curso")
        return await self.post(
            "/api/cursos/crear",
            json_data=curso_data,
        )

    async def update_curso(self, curso_id: int, curso_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing curso."""
        logger.info(f"Calling DjangoBackend.update_curso: {curso_id}")
        return await self.post(
            f"/api/cursos/actualizar/{curso_id}",
            json_data=curso_data,
        )

    async def get_foros(self, curso_id: Optional[int] = None) -> Dict[str, Any]:
        """Get foros, optionally filtered by curso."""
        logger.info(f"Calling DjangoBackend.get_foros for curso: {curso_id}")
        params = {"curso_id": curso_id} if curso_id else {}
        return await self.get("/api/foros/listar", params=params)

    async def health_check(self) -> bool:
        """Check if Django backend is healthy."""
        try:
            response = await self.get("/health/")
            return response.get("status") == "ok"
        except Exception:
            return False


class ValidationServiceClient(MicroserviceClient):
    """Client for the Validation microservice (ms_validation)."""

    async def validate_process(
        self, validation_request: ValidationRequest
    ) -> Dict[str, Any]:
        """Validate a process against business rules."""
        logger.info("Calling ValidationService.validate_process")
        return await self.post(
            "/validate",
            json_data=validation_request.model_dump(),
        )

    async def get_rules(self) -> Dict[str, Any]:
        """Get available validation rules."""
        logger.info("Calling ValidationService.get_rules")
        return await self.get("/rules")

    async def validate_batch(
        self, requests: list[ValidationRequest]
    ) -> Dict[str, Any]:
        """Validate multiple processes in batch."""
        logger.info(f"Calling ValidationService.validate_batch with {len(requests)} items")
        return await self.post(
            "/validate-batch",
            json_data={"items": [r.model_dump() for r in requests]},
        )


class BackendAPIClient(MicroserviceClient):
    """Client for the Backend API microservice (ia_service_core)."""

    async def analyze_content(
        self, analysis_request: AnalysisRequest
    ) -> Dict[str, Any]:
        """Analyze content using RAG or other analysis methods."""
        logger.info(f"Calling BackendAPI.analyze_content ({analysis_request.analysis_type})")
        return await self.post(
            "/agent/analyze",
            json_data=analysis_request.model_dump(),
        )

    async def chat_with_rag(
        self, question: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a question to the RAG chatbot."""
        logger.info("Calling BackendAPI.chat_with_rag")
        return await self.post(
            "/agent/chat",
            json_data={
                "question": question,
                "context": context or {},
            },
        )

    async def ingest_document(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingest a document for RAG."""
        logger.info(f"Calling BackendAPI.ingest_document: {file_path}")
        return await self.post(
            "/agent/ingest",
            json_data={
                "file_path": file_path,
                "metadata": metadata or {},
            },
        )

    async def search_documents(
        self, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Search ingested documents."""
        logger.info(f"Calling BackendAPI.search_documents: {query}")
        return await self.get(
            "/agent/search",
            params={"q": query, "limit": limit},
        )


class MicroserviceDBClient(MicroserviceClient):
    """Client for the Microservice DB (microservice_db)."""

    async def store_result(
        self, collection: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a result in the database."""
        logger.info(f"Calling MicroserviceDB.store_result in {collection}")
        return await self.post(
            f"/{collection}/store",
            json_data=data,
        )

    async def retrieve_result(
        self, collection: str, result_id: str
    ) -> Dict[str, Any]:
        """Retrieve a result from the database."""
        logger.info(f"Calling MicroserviceDB.retrieve_result from {collection}")
        return await self.get(f"/{collection}/{result_id}")

    async def query_results(
        self, collection: str, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query results from a collection."""
        logger.info(f"Calling MicroserviceDB.query_results from {collection}")
        return await self.get(
            f"/{collection}/query",
            params={"filters": str(filters or {})},
        )

    async def delete_result(self, collection: str, result_id: str) -> Dict[str, Any]:
        """Delete a result from the database."""
        logger.info(f"Calling MicroserviceDB.delete_result from {collection}")
        return await self.delete(f"/{collection}/{result_id}")

    async def list_collections(self) -> Dict[str, Any]:
        """List available collections."""
        logger.info("Calling MicroserviceDB.list_collections")
        return await self.get("/collections")


class ServiceRegistry:
    """Registry of all microservice clients."""

    def __init__(self, validation_url: str, backend_url: str, db_url: str, django_url: str):
        self.validation = ValidationServiceClient(
            service_name="ms_validation",
            base_url=validation_url,
        )
        self.backend = BackendAPIClient(
            service_name="ia_service_core",
            base_url=backend_url,
        )
        self.database = MicroserviceDBClient(
            service_name="microservice_db",
            base_url=db_url,
        )
        self.django = DjangoBackendClient(
            service_name="django_backend",
            base_url=django_url,
        )

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all services."""
        logger.info("Performing health check on all services")
        results = {}
        for name, client in [
            ("validation", self.validation),
            ("backend", self.backend),
            ("database", self.database),
            ("django", self.django),
        ]:
            try:
                results[name] = await client.health_check()
            except Exception as e:
                logger.warning(f"Health check failed for {name}: {str(e)}")
                results[name] = False
        return results

    async def close_all(self) -> None:
        """Close all service connections."""
        logger.info("Closing all microservice clients")
        await self.validation.close()
        await self.backend.close()
        await self.database.close()
        await self.django.close()
