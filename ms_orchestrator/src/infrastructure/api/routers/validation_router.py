"""Validation orchestration router."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
import uuid

from ms_orchestrator.src.domain import (
    ValidationRequest,
    ServiceResponse,
)
from ms_orchestrator.src.application import ValidationOrchestrationUseCase
from ms_orchestrator.src.infrastructure.external.clients import ServiceRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestrate/validation", tags=["Validation Orchestration"])


# Dependency injection
async def get_validation_use_case(
    service_registry: ServiceRegistry = Depends(),
) -> ValidationOrchestrationUseCase:
    """Get validation orchestration use case."""
    return ValidationOrchestrationUseCase(service_registry)


@router.post(
    "/validate",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate a process with orchestration",
    description="Validates a process against business rules with optional analysis",
)
async def validate_with_context(
    request: ValidationRequest,
    use_case: ValidationOrchestrationUseCase = Depends(get_validation_use_case),
) -> ServiceResponse:
    """
    Validate a process with automatic context gathering and analysis.

    This endpoint orchestrates the validation process by:
    1. Sending the process to the validation service
    2. If validation fails, optionally running analysis
    3. Combining results for comprehensive evaluation
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Validation orchestration request: {request_id}",
        extra={"request_id": request_id},
    )

    try:
        result = await use_case.validate_with_context(request)

        return ServiceResponse(
            status="success",
            data=result,
            request_id=request_id,
        )

    except Exception as e:
        logger.error(
            f"Validation orchestration failed: {str(e)}",
            extra={"request_id": request_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation orchestration failed: {str(e)}",
        )


@router.post(
    "/validate-batch",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate multiple processes",
    description="Batch validation of multiple processes",
)
async def validate_batch(
    requests: list[ValidationRequest],
    use_case: ValidationOrchestrationUseCase = Depends(get_validation_use_case),
) -> ServiceResponse:
    """
    Validate multiple processes in a batch operation.

    This endpoint validates multiple processes and returns results for each.
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Batch validation request: {len(requests)} items",
        extra={"request_id": request_id},
    )

    try:
        results = []
        for validation_request in requests:
            result = await use_case.validate_with_context(validation_request)
            results.append(result)

        return ServiceResponse(
            status="success",
            data={"items": results, "count": len(results)},
            request_id=request_id,
        )

    except Exception as e:
        logger.error(
            f"Batch validation failed: {str(e)}",
            extra={"request_id": request_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch validation failed: {str(e)}",
        )
