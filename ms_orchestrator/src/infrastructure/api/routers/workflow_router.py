"""Workflow orchestration router."""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
import uuid

from ms_orchestrator.src.domain import (
    OrchestratedWorkflow,
    WorkflowExecutionResponse,
    ServiceResponse,
)
from ms_orchestrator.src.application import WorkflowOrchestrationUseCase
from ms_orchestrator.src.infrastructure.external.clients import ServiceRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestrate/workflows", tags=["Workflow Orchestration"])


# Dependency injection
async def get_workflow_use_case(
    service_registry: ServiceRegistry = Depends(),
) -> WorkflowOrchestrationUseCase:
    """Get workflow orchestration use case."""
    return WorkflowOrchestrationUseCase(service_registry)


@router.post(
    "/execute",
    response_model=WorkflowExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute an orchestrated workflow",
    description="Execute a complex multi-step workflow across microservices",
)
async def execute_workflow(
    workflow: OrchestratedWorkflow,
    use_case: WorkflowOrchestrationUseCase = Depends(get_workflow_use_case),
) -> WorkflowExecutionResponse:
    """
    Execute a complex workflow that spans multiple microservices.

    This endpoint orchestrates multi-step workflows by:
    1. Accepting a workflow definition with sequential or parallel steps
    2. Executing steps across different microservices
    3. Handling errors and retries
    4. Returning consolidated results

    **Workflow Step Structure:**
    ```json
    {
      "service": "validation|backend_api|database",
      "action": "validate_process|analyze_content|store|etc",
      "parameters": {...}
    }
    ```

    **Execution Modes:**
    - `parallel: false` (default): Steps execute sequentially
    - `parallel: true`: Steps execute concurrently
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Workflow execution request: {workflow.workflow_name}",
        extra={"request_id": request_id, "workflow_id": workflow.workflow_id},
    )

    try:
        response = await use_case.execute_workflow(workflow)
        return response

    except Exception as e:
        logger.error(
            f"Workflow execution failed: {str(e)}",
            extra={
                "request_id": request_id,
                "workflow_id": workflow.workflow_id,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.get(
    "/templates",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get workflow templates",
    description="List available workflow templates",
)
async def get_workflow_templates() -> ServiceResponse:
    """
    Get available workflow templates.

    Returns predefined workflow templates for common orchestration patterns.
    """
    logger.info("Fetching workflow templates")

    templates = {
        "teacher_evaluation": {
            "name": "Teacher Evaluation Pipeline",
            "description": "Complete pipeline for teacher evaluation",
            "steps": [
                {
                    "service": "validation",
                    "action": "validate_process",
                    "description": "Validate evaluation process",
                },
                {
                    "service": "backend_api",
                    "action": "analyze_content",
                    "description": "Analyze evaluation content",
                },
                {
                    "service": "database",
                    "action": "store",
                    "description": "Store evaluation results",
                },
            ],
        },
        "document_processing": {
            "name": "Document Processing Pipeline",
            "description": "Complete document ingestion and analysis pipeline",
            "steps": [
                {
                    "service": "backend_api",
                    "action": "ingest_document",
                    "description": "Ingest document",
                },
                {
                    "service": "backend_api",
                    "action": "analyze_content",
                    "description": "Analyze document content",
                },
                {
                    "service": "database",
                    "action": "store",
                    "description": "Store document analysis",
                },
            ],
        },
        "rule_validation_analysis": {
            "name": "Rule Validation & Analysis",
            "description": "Validate against rules and analyze failures",
            "steps": [
                {
                    "service": "validation",
                    "action": "validate_process",
                    "description": "Validate against business rules",
                },
                {
                    "service": "backend_api",
                    "action": "analyze_content",
                    "description": "Analyze validation results",
                },
            ],
        },
    }

    return ServiceResponse(
        status="success",
        data=templates,
    )
