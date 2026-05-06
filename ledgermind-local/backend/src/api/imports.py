from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from ..ingestion.service import IngestionService

router = APIRouter(prefix="/api/import", tags=["Import"])
ingestion_service = IngestionService()

@router.post("/preview")
async def preview_import(
    file: UploadFile = File(...),
    source_bank: Optional[str] = Form("auto")
):
    content = await file.read()
    try:
        preview_data = ingestion_service.preview(file.filename, content, source_bank)
        return preview_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("")
async def execute_import(
    file: UploadFile = File(...),
    source_bank: Optional[str] = Form("auto"),
    account_name: Optional[str] = Form(None)
):
    content = await file.read()
    try:
        import_result = ingestion_service.process_import(file.filename, content, source_bank, account_name)
        return import_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # For serious errors
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
