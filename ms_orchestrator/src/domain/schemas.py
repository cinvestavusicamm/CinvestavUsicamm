"""Domain models and schemas for the Orchestrator."""

from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────
# Request Models
# ─────────────────────────────────────────────────────────────────────


class ValidationRequest(BaseModel):
    """Request model for validation service."""

    process_description: str = Field(..., description="Process to validate")
    rules_context: Optional[Dict[str, Any]] = Field(
        None, description="Context for validation rules"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "process_description": "Docente evaluando estudiantes",
                "rules_context": {"course_id": "123", "semester": "2024-1"},
                "metadata": {"source": "escalafon_system"},
            }
        }


class AnalysisRequest(BaseModel):
    """Request model for AI analysis service."""

    content: str = Field(..., description="Content to analyze")
    analysis_type: str = Field(..., description="Type of analysis (rag, classification, etc)")
    context: Optional[Dict[str, Any]] = Field(None, description="Analysis context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Documento de evaluación docente",
                "analysis_type": "rag",
                "context": {"model": "phi-3"},
            }
        }


class DocumentRequest(BaseModel):
    """Request model for document processing."""

    document_id: str = Field(..., description="Unique document identifier")
    operation: str = Field(..., description="Operation to perform (ingest, search, delete)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "operation": "ingest",
                "parameters": {"document_type": "pdf", "user_id": "user_456"},
            }
        }


class OrchestratedWorkflow(BaseModel):
    """Complex workflow orchestration request."""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    workflow_name: str = Field(..., description="Human-readable workflow name")
    steps: List[Dict[str, Any]] = Field(
        ..., description="Sequential steps of the workflow"
    )
    params: Optional[Dict[str, Any]] = Field(None, description="Workflow parameters")
    parallel: bool = Field(
        False, description="Whether steps should execute in parallel"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_789",
                "workflow_name": "Teacher Evaluation Pipeline",
                "steps": [
                    {"service": "validation", "action": "validate_process"},
                    {"service": "backend_api", "action": "analyze_content"},
                    {"service": "microservice_db", "action": "store_results"},
                ],
                "parallel": False,
            }
        }


# ─────────────────────────────────────────────────────────────────────
# Response Models
# ─────────────────────────────────────────────────────────────────────


class ServiceResponse(BaseModel):
    """Generic service response wrapper."""

    status: str = Field(..., description="Response status (success, error, pending)")
    data: Optional[Dict[str, Any]] = Field(None, description="Response payload")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if any")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    request_id: Optional[str] = Field(None, description="Trace request ID")


class OrchestratorHealthResponse(BaseModel):
    """Health check response for orchestrator."""

    status: str = Field(..., description="Overall orchestrator status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Health check time"
    )
    services: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Status of dependent services"
    )


class WorkflowExecutionResponse(BaseModel):
    """Response for workflow execution."""

    workflow_id: str = Field(..., description="Workflow ID")
    execution_id: str = Field(..., description="Unique execution instance ID")
    status: str = Field(..., description="Execution status (running, completed, failed)")
    results: List[Dict[str, Any]] = Field(
        default_factory=list, description="Results from each step"
    )
    errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Errors encountered"
    )
    started_at: datetime = Field(..., description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution end time")


# ─────────────────────────────────────────────────────────────────────
# Event Models (for internal pub/sub if implemented)
# ─────────────────────────────────────────────────────────────────────


class OrchestratorEvent(BaseModel):
    """Event model for orchestrator internal pub/sub."""

    event_id: str = Field(..., description="Unique event ID")
    event_type: str = Field(..., description="Type of event")
    source_service: str = Field(..., description="Service that generated the event")
    target_services: List[str] = Field(
        default_factory=list, description="Services that should handle this event"
    )
    payload: Dict[str, Any] = Field(..., description="Event payload")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )
    priority: int = Field(default=0, description="Event priority (0=low, 10=high)")
