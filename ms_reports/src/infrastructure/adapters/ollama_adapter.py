"""infrastructure.llm.ollama_adapter
Adaptador de IA con validación estricta (Pydantic). 
Garantiza que el LLM entregue un esquema determinista para el motor de renderizado.
"""
import json
import re
import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

# FIJADO: Importación sin el prefijo 'src.'
from infrastructure.config.settings import settings

logger = logging.getLogger("ms_reports.ollama")

# --- CONTRATOS DE DISEÑO (ANTI-ALUCINACIÓN) ---
class StyleSchema(BaseModel):
    primary_color: str = Field(default="#691C32")
    secondary_color: str = Field(default="#BC955C")
    watermark_url: Optional[str] = Field(default=None)

class HeaderSchema(BaseModel):
    title: str = Field(default="Reporte Oficial")
    subtitle: str = Field(default="")
    logo_url: Optional[str] = Field(default=None)

class SectionSchema(BaseModel):
    type: str = Field(..., description="Tipos soportados: 'key_value', 'text', 'chart'")
    title: str = Field(default="")
    content: Optional[str] = Field(default=None)
    data: Optional[Dict[str, Any]] = Field(default=None)

class ReportLayoutSchema(BaseModel):
    style: StyleSchema = Field(default_factory=StyleSchema)
    header: HeaderSchema = Field(default_factory=HeaderSchema)
    sections: List[SectionSchema] = Field(default_factory=list)
    footer_text: str = Field(default="Documento generado automáticamente por EscalafonIA.")

class OllamaAdapter:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.llm_model = settings.OLLAMA_LLM_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self.timeout = 120.0

    def get_embedding(self, text: str) -> list:
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {"model": self.embed_model, "prompt": text}
            resp = httpx.post(url, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.json().get("embedding", [])
        except Exception as e:
            logger.error(f"Error Ollama embedding: {e}")
        return []

    def _sanitize_json(self, raw_text: str) -> str:
        """Limpia la respuesta del LLM para extraer únicamente el objeto JSON.
        Mejorado para resistir inyecciones de Markdown típicas en modelos pequeños.
        """
        # Quitar bloques de markdown explícitos
        text = raw_text.replace("```json", "").replace("```", "").strip()
        
        # Buscar el bloque principal del JSON
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text

    def generate_universal_layout(self, context_rules: str, payload_data: dict) -> dict:
        prompt = f"""
        ACTÚA COMO UN PARSER DE JSON ESTRICTO. 
        Tu única función es tomar los datos de entrada y las reglas, y combinarlos en UN SOLO OBJETO JSON.
        
        REGLAS DE DISEÑO:
        {context_rules}
        
        DATOS DE ENTRADA:
        {json.dumps(payload_data, ensure_ascii=False)}
        
        INSTRUCCIONES CRÍTICAS:
        1. Debes generar un JSON con esta estructura exacta. NO cambies los nombres de las llaves principales ('style', 'header', 'sections', 'footer_text').
        2. Dentro de 'sections', cada objeto DEBE tener una llave 'type' que solo puede ser "key_value", "text" o "chart".
        3. Pon los "datos_inventados" en una sección "key_value".
        4. Pon las "metricas_ejemplo" en una sección "chart".
        5. Devuelve SÓLO el código JSON. Nada de saludos, ni markdown, ni explicaciones.

        EJEMPLO DE SALIDA ESPERADA:
        {{
            "style": {{
                "primary_color": "#9D2449",
                "secondary_color": "#BC955C",
                "watermark_url": "https://framework-gb.cdn.gob.mx/landing/img/escudo.svg"
            }},
            "header": {{
                "title": "SECRETARÍA DE EDUCACIÓN PÚBLICA",
                "subtitle": "Sistema EscalafonIA",
                "logo_url": "https://framework-gb.cdn.gob.mx/landing/img/logoheader.svg"
            }},
            "sections": [
                {{
                    "type": "key_value",
                    "title": "Datos del Trámite",
                    "data": {{"Folio": "123", "Estado": "Aprobado"}}
                }},
                {{
                    "type": "chart",
                    "title": "Métricas de Validación",
                    "data": {{"Puntaje": 85, "Antigüedad": 10}}
                }}
            ],
            "footer_text": "Este documento fue generado automatizadamente."
        }}
        """
        
        try:
            url = f"{self.base_url}/api/generate"
            req_payload = {
                "model": self.llm_model, 
                "prompt": prompt, 
                "stream": False, 
                # Quitamos format="json" temporalmente. A veces confunde a phi3 en tareas complejas.
            }
            resp = httpx.post(url, json=req_payload, timeout=self.timeout)
            
            if resp.status_code == 200:
                raw_output = resp.json().get("response", "{}")
                
                logger.info("=== RESPUESTA CRUDA DEL LLM ===")
                logger.info(raw_output)
                logger.info("===============================")
                
                clean_json = self._sanitize_json(raw_output)
                data = json.loads(clean_json)
                
                validated_model = ReportLayoutSchema(**data)
                return validated_model.model_dump()
                
        except ValidationError as ve:
            logger.error(f"Pydantic rechazó el JSON. Errores de esquema: {ve}")
        except json.JSONDecodeError as je:
            logger.error(f"El LLM no devolvió un JSON válido. Error de sintaxis: {je}")
        except Exception as e:
            logger.error(f"Fallo general en generación de layout: {e}")
            
        return ReportLayoutSchema(
            header=HeaderSchema(title="Reporte EscalafonIA", subtitle="Modo Contingencia"),
            sections=[SectionSchema(type="text", title="Error", content="No se pudo estructurar el diseño.")],
            footer_text=":)"
        ).model_dump()