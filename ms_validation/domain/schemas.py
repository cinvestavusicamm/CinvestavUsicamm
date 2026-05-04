"""ms_validation.domain.schemas
Modelos Pydantic para el contrato estricto de la API de EscalafonIA.
Cumple con la normativa MoProSoft para asegurar trazabilidad.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# ──────────────────────────────────────────────
# REQUEST — Trámite de Escalafón a evaluar
# ──────────────────────────────────────────────

class ProcessInput(BaseModel):
    """
    Representa un proceso o trámite de promoción docente para ser validado
    contra la normativa de EscalafonIA (SEP/USICAMM) inyectada vía RAG.
    """

    process_id: str = Field(
        ...,
        description="ID único del trámite o solicitud.",
        examples=["ESC-PROM-2026-001"],
    )
    process_name: str = Field(
        ...,
        description="Nombre del trámite de promoción o reconocimiento.",
        examples=["Promoción Vertical - Educación Básica"],
    )
    description: str = Field(
        ...,
        description="Descripción detallada de la trayectoria o proceso propuesto.",
        examples=[
            "Solicitud de ascenso a años de antigüedad y maestría en pedagogía."
        ],
    )
    category: str = Field(
        default="promocion",
        description="Categoría: 'promocion_vertical', 'promocion_horizontal', 'reconocimiento', 'reubicacion'.",
        examples=["promocion_vertical"],
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="Actores involucrados (ej. Docente, ATP, Director).",
        examples=[["Docente", "Comité de Escalafón"]],
    )
    activities: Optional[List[str]] = Field(
        default=None,
        description="Requisitos o pasos cumplidos por el docente.",
        examples=[
            [
                "Entrega de constancia de antigüedad",
                "Acreditación de cursos de formación continua",
                "Validación de grado académico",
            ]
        ],
    )

# ──────────────────────────────────────────────
# RESPONSE — Resultado de la validación
# ──────────────────────────────────────────────

class Violation(BaseModel):
    """Incumplimiento de un requisito normativo de promoción."""
    rule: str = Field(..., description="Artículo o lineamiento de la normativa violado.")
    detail: str = Field(..., description="Explicación de por qué el docente no cumple el requisito.")
    severity: str = Field(
        default="high",
        description="Gravedad: 'low' (subsanable), 'medium', 'high' (rechazo total).",
    )

class ValidationResult(BaseModel):
    """Resultado estricto de la evaluación RAG para EscalafonIA."""
    is_valid: bool = Field(..., description="True si el trámite cumple con la normativa vigente.")
    violations: List[Violation] = Field(default_factory=list)
    missing_resources: List[str] = Field(
        default_factory=list,
        description="Documentación faltante (ej. Título, Constancia de servicio).",
    )

class ValidationResponse(BaseModel):
    """Respuesta final del API."""
    process_id: str
    result: ValidationResult
    sources_used: int = Field(default=0, description="Fragmentos de leyes/reglas consultados.")