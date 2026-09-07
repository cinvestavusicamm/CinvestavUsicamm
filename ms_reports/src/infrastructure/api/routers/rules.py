"""app.api.v1.rules
Endpoints para que el Administrador gestione los PDFs de reglas (RAG).
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import io
from pypdf import PdfReader
from src.infrastructure.adapters.qdrant_adapter import QdrantAdapter

router = APIRouter()

def get_qdrant() -> QdrantAdapter:
    return QdrantAdapter()

@router.post("/upload", summary="Sube un PDF con reglas de diseño para un perfil")
async def upload_pdf_rules(
    profile_name: str = Form(..., description="Ej. SEP_Oficial"),
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")
    
    try:
        # 1. Leer el archivo PDF en memoria
        content = await file.read()
        reader = PdfReader(io.BytesIO(content))
        
        # 2. Extraer todo el texto
        pdf_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pdf_text += extracted + "\n"
                
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="El PDF está vacío o es una imagen escaneada sin texto.")
            
        # 3. Mandar a Qdrant
        qdrant = get_qdrant()
        qdrant.upsert_rule(profile_name, pdf_text)
        
        return {
            "status": "success", 
            "message": f"Reglas inyectadas en Qdrant para el perfil '{profile_name}'",
            "extracted_characters": len(pdf_text)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{profile_name}", summary="Elimina las reglas de un perfil")
def delete_rules(profile_name: str):
    try:
        qdrant = get_qdrant()
        qdrant.delete_rule(profile_name)
        return {"status": "success", "message": f"Reglas de '{profile_name}' eliminadas de Qdrant."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))