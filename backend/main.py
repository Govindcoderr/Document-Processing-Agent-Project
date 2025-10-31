# backend/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.ocr_extractor import extract_text_from_image
from backend.llm_extractor import extract_fields
from backend.data_validator import validate_invoice_data
from backend.db import save_invoice_to_db
from backend.erp_integration import push_to_erp
import logging

app = FastAPI(title="Document Processing Agent")
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/process-invoice/")
async def process_invoice(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        raw_text = extract_text_from_image(contents)  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR error: {e}")
    
    print("📄 Raw OCR Text:", raw_text)  # Debugging line

    fields = extract_fields(raw_text)

    try:
        validated = validate_invoice_data(fields)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    row_id = save_invoice_to_db(validated)
    erp_resp = push_to_erp(validated)

    return {
        "status": "success",
        "data": validated,
        "db_id": row_id,
        "erp_response": erp_resp
    }
