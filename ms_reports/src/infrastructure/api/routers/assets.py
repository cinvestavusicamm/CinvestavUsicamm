"""infrastructure.api.routers.assets
Endpoints para la gestión de activos estáticos (Logos institucionales, marcas de agua).
Permite a los administradores actualizar la identidad visual sin tocar código.
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter()

# La ruta debe coincidir con el volumen que montamos en docker-compose
ASSETS_DIR = "/srv/ms3_reports/static/assets/logos"

@router.post("/logos/{institution_id}", summary="Sube o reemplaza un logo institucional")
async def upload_logo(institution_id: str, file: UploadFile = File(...)):
    """
    Recibe una imagen (preferiblemente PNG transparente) y la guarda 
    con el ID de la institución para inyección automática en los reportes.
    """
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes PNG o JPEG.")
    
    # Aseguramos que la carpeta exista
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # Forzamos la extensión .png por estandarización en ReportBuilder
    file_path = os.path.join(ASSETS_DIR, f"{institution_id}.png")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": f"Logo para '{institution_id}' guardado exitosamente."}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")

@router.delete("/logos/{institution_id}", summary="Elimina un logo institucional")
async def delete_logo(institution_id: str):
    file_path = os.path.join(ASSETS_DIR, f"{institution_id}.png")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"Logo '{institution_id}' eliminado. El sistema usará default.png."}
    
    raise HTTPException(status_code=404, detail="Logo no encontrado.")