from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from application.use_cases.agent.ingest_doc import IngestDocUseCase
from infrastructure.api.dependencies import get_ingest_use_case

router = APIRouter()

@router.post("/upload-pdf")
async def upload_document(
    file: UploadFile = File(...),
    use_case: IngestDocUseCase = Depends(get_ingest_use_case)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo archivos PDF")
        
    try:
        content = await file.read()
        result = await use_case.run(content, file.filename)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))