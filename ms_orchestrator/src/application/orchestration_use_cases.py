"""Orchestration use cases - Application layer business logic."""

import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from ms_orchestrator.src.domain import (
    ValidationRequest,
    AnalysisRequest,
    OrchestratedWorkflow,
    WorkflowExecutionResponse,
    ServiceResponse,
)
from ms_orchestrator.src.domain.exceptions import WorkflowExecutionError
from ms_orchestrator.src.infrastructure.external.clients import ServiceRegistry

logger = logging.getLogger(__name__)


class ValidationOrchestrationUseCase:
    """Use case for orchestrating validation operations."""

    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry

    async def validate_with_context(
        self, validation_request: ValidationRequest
    ) -> Dict[str, Any]:
        """
        Validate a process with additional context gathering.

        Combines validation service with backend analysis for comprehensive
        process evaluation.
        """
        logger.info(f"Starting validation orchestration for: {validation_request.process_description}")

        # Step 1: Validate against rules
        validation_result = await self.service_registry.validation.validate_process(
            validation_request
        )

        logger.info(f"Validation completed: {validation_result}")

        # Step 2: If validation failed, optionally run analysis
        if validation_result.get("status") == "failed":
            try:
                logger.info("Running analysis for failed validation")
                analysis_request = AnalysisRequest(
                    content=validation_request.process_description,
                    analysis_type="diagnostic",
                    context={
                        "validation_errors": validation_result.get("errors", []),
                        "rules_applied": validation_result.get("rules_applied", []),
                    },
                )
                analysis_result = await self.service_registry.backend.analyze_content(
                    analysis_request
                )
                validation_result["analysis"] = analysis_result
            except Exception as e:
                logger.warning(f"Analysis failed: {str(e)}")
                validation_result["analysis"] = {"error": str(e)}

        return validation_result


class AnalysisOrchestrationUseCase:
    """Use case for orchestrating analysis operations."""

    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry

    async def analyze_and_store(
        self, analysis_request: AnalysisRequest
    ) -> Dict[str, Any]:
        """
        Analyze content and store the results.

        Performs analysis through the backend and stores results in the database.
        """
        logger.info(f"Starting analysis orchestration: {analysis_request.analysis_type}")

        # Step 1: Analyze
        analysis_result = await self.service_registry.backend.analyze_content(
            analysis_request
        )

        # Step 2: Store results
        try:
            logger.info("Storing analysis results")
            storage_result = await self.service_registry.database.store_result(
                collection="analysis_results",
                data={
                    "analysis_type": analysis_request.analysis_type,
                    "content_preview": analysis_request.content[:100],
                    "result": analysis_result,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            analysis_result["storage_id"] = storage_result.get("id")
        except Exception as e:
            logger.error(f"Failed to store results: {str(e)}")
            analysis_result["storage_error"] = str(e)

        return analysis_result


class WorkflowOrchestrationUseCase:
    """Use case for complex workflow orchestration."""

    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry

    async def execute_workflow(
        self, workflow: OrchestratedWorkflow
    ) -> WorkflowExecutionResponse:
        """
        Execute a complex multi-step workflow.

        Orchestrates sequential or parallel execution of workflow steps across
        multiple microservices.
        """
        execution_id = str(uuid.uuid4())
        logger.info(
            f"Starting workflow execution: {workflow.workflow_name}",
            extra={"workflow_id": workflow.workflow_id, "execution_id": execution_id},
        )

        execution_response = WorkflowExecutionResponse(
            workflow_id=workflow.workflow_id,
            execution_id=execution_id,
            status="running",
            started_at=datetime.utcnow(),
        )

        try:
            if workflow.parallel:
                # Execute steps in parallel
                execution_response.results = await self._execute_parallel_steps(
                    workflow.steps, workflow.params or {}
                )
            else:
                # Execute steps sequentially
                execution_response.results = await self._execute_sequential_steps(
                    workflow.steps, workflow.params or {}
                )

            execution_response.status = "completed"

        except WorkflowExecutionError as e:
            logger.error(
                f"Workflow execution failed: {str(e)}",
                extra={
                    "workflow_id": workflow.workflow_id,
                    "execution_id": execution_id,
                    "step": e.step,
                },
            )
            execution_response.status = "failed"
            execution_response.errors.append(
                {
                    "step": e.step,
                    "error": e.error_details,
                }
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in workflow execution: {str(e)}",
                extra={
                    "workflow_id": workflow.workflow_id,
                    "execution_id": execution_id,
                },
            )
            execution_response.status = "failed"
            execution_response.errors.append(
                {"error": str(e), "type": type(e).__name__}
            )

        finally:
            execution_response.completed_at = datetime.utcnow()

        logger.info(
            f"Workflow execution completed with status: {execution_response.status}",
            extra={"workflow_id": workflow.workflow_id},
        )

        return execution_response

    async def _execute_sequential_steps(
        self, steps: List[Dict[str, Any]], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute workflow steps sequentially."""
        results = []
        for step_idx, step in enumerate(steps):
            try:
                logger.info(f"Executing step {step_idx + 1}/{len(steps)}")
                result = await self._execute_step(step, params)
                results.append(result)
            except Exception as e:
                raise WorkflowExecutionError(
                    workflow_id="unknown",
                    step=step_idx,
                    error_details=str(e),
                ) from e
        return results

    async def _execute_parallel_steps(
        self, steps: List[Dict[str, Any]], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute workflow steps in parallel."""
        import asyncio

        logger.info(f"Executing {len(steps)} steps in parallel")
        tasks = [
            self._execute_step(step, params) for step in steps
        ]

        try:
            results = await asyncio.gather(*tasks)
            return results
        except Exception as e:
            raise WorkflowExecutionError(
                workflow_id="unknown",
                step=-1,
                error_details=f"Parallel execution failed: {str(e)}",
            ) from e

    async def _execute_step(
        self, step: Dict[str, Any], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        service = step.get("service", "").lower()
        action = step.get("action", "").lower()
        step_params = step.get("parameters", params)

        logger.debug(f"Executing step: {service}.{action}")

        # Route to appropriate service
        if service == "validation":
            if action == "validate_process":
                validation_req = ValidationRequest(**step_params)
                return await self.service_registry.validation.validate_process(
                    validation_req
                )

        elif service == "backend_api" or service == "backend":
            if action == "analyze_content":
                analysis_req = AnalysisRequest(**step_params)
                return await self.service_registry.backend.analyze_content(analysis_req)
            elif action == "chat":
                return await self.service_registry.backend.chat_with_rag(
                    question=step_params.get("question"),
                    context=step_params.get("context"),
                )

        elif service == "database" or service == "microservice_db":
            if action == "store":
                return await self.service_registry.database.store_result(
                    collection=step_params.get("collection"),
                    data=step_params.get("data"),
                )
            elif action == "retrieve":
                return await self.service_registry.database.retrieve_result(
                    collection=step_params.get("collection"),
                    result_id=step_params.get("result_id"),
                )

        raise ValueError(f"Unknown service or action: {service}.{action}")
