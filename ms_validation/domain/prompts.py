"""ms_validation.domain.prompts

Plantillas de prompts reforzadas para la validación determinista de EscalafonIA.
Diseñadas para evitar comentarios ilegales en la salida JSON de modelos pequeños (Phi-3).
"""

from .schemas import ProcessInput

# ──────────────────────────────────────────────
# SYSTEM PROMPT — El Motor de Cumplimiento Legal
# ──────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Actúa como un Auditor Normativo de Alto Nivel para el sistema EscalafonIA. "
    "Tu objetivo es realizar una VALIDACIÓN CRUZADA entre un TRÁMITE DOCENTE (Evidencia) "
    "y un CONTEXTO NORMATIVO (Leyes/Reglas) proporcionado.\n\n"
    
    "DIRECTRICES OBLIGATORIAS CRÍTICAS:\n"
    "1. RIGOR NORMATIVO: Solo puedes validar el trámite basándote en el CONTEXTO NORMATIVO adjunto. "
    "Si el contexto exige algo que el trámite no presenta, márcalo como incumplimiento.\n"
    "2. CITACIÓN TEXTUAL: En cada elemento de 'violations', el campo 'detail' DEBE incluir una cita "
    "textual breve del fragmento de la ley que se está incumpliendo, seguida de la explicación.\n"
    "3. FORMATO JSON PURO: Tu salida debe ser ÚNICAMENTE un objeto JSON. PROHIBIDO incluir comentarios "
    "de código (como // o /* */) dentro o fuera del JSON. No incluyas explicaciones previas ni posteriores.\n"
    "4. DETERMINISMO: Evalúa cada actividad y descripción estrictamente contra las reglas de la normativa.\n\n"
    
    "ESQUEMA JSON DE SALIDA ESPERADO:\n"
    "{\n"
    '  "is_valid": <boolean>,\n'
    '  "violations": [\n'
    '    {\n'
    '      "rule": "<Referencia al Artículo/Sección de la ley>",\n'
    '      "detail": "<Cita textual de la ley + explicación del incumplimiento>",\n'
    '      "severity": "low|medium|high"\n'
    '    }\n'
    '  ],\n'
    '  "missing_resources": ["<Nombre del documento o requisito faltante según la ley>"],\n'
    '  "observations": "<Consejos constructivos para que el docente mejore su trámite o resuelva las faltas>"\n'
    "}\n\n"
    
    "CRITERIO DE GRAVEDAD:\n"
    "- high: Falta de requisitos de ley o incumplimiento de criterios de elegibilidad.\n"
    "- medium: Documentación incompleta o ambigua.\n"
    "- low: Observaciones administrativas o sugerencias de mejora."
)

# ──────────────────────────────────────────────
# USER PROMPT builder
# ──────────────────────────────────────────────

def build_validation_prompt(process: ProcessInput, rag_context: str) -> str:
    """
    Construye un prompt de validación robusto inyectando la normativa dinámica.
    """
    
    # Preparamos la lista de actividades para el prompt
    activities_list = "\n".join([f"- {act}" for act in (process.activities or [])])
    
    user_content = (
        "### 1. MARCO NORMATIVO APLICABLE (Inyectado vía RAG):\n"
        "--------------------------------------------------\n"
        f"{rag_context}\n"
        "--------------------------------------------------\n\n"
        
        "### 2. EXPEDIENTE DEL TRÁMITE A EVALUAR:\n"
        f"  - ID: {process.process_id}\n"
        f"  - Proceso: {process.process_name}\n"
        f"  - Categoría: {process.category}\n"
        f"  - Descripción del solicitante: {process.description}\n"
        f"  - Evidencias/Actividades registradas:\n{activities_list}\n\n"
        
        "### 3. TAREA:\n"
        "Analiza si las 'Evidencias' y la 'Descripción' del trámite satisfacen los requisitos "
        "descritos en el 'MARCO NORMATIVO'.\n\n"
        "Genera ÚNICAMENTE el dictamen JSON ahora (SIN COMENTARIOS // ni texto adicional):"
    )

    return f"{SYSTEM_PROMPT}\n\n{user_content}"