from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.ocr_extractor import extract_text_from_image
from backend.llm_extractor import extract_fields
from backend.data_validator import validate_invoice_data
from backend.db import save_invoice_to_db
from backend.erp_integration import push_to_erp
import logging

# ---------------- App Setup ----------------
app = FastAPI(title="Document Processing Agent")
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Main Route ----------------
@app.post("/process-invoice/")
async def process_invoice(file: UploadFile = File(...)):
    """
    Full pipeline:
      1️ OCR → Extract text (PDF/Image)
      2️ LLM/Regex → Extract fields
      3️ Validate fields
      4️ Save to SQLite
      5️ Push to ERPNext (REST API)
    """
    # Step 1: OCR Extraction
    try:
        contents = await file.read()
        raw_text = extract_text_from_image(contents)
        logging.info("OCR extraction completed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR error: {e}")

    print("\n Raw OCR Text:\n", raw_text[:1000])  # Debug first 1000 chars

    # Step 2: Field Extraction (LLM or Regex)
    try:
        fields = extract_fields(raw_text)
        logging.info(f"Extracted Fields: {fields}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Field extraction error: {e}")

    # Step 3: Validation
    try:
        validated = validate_invoice_data(fields)
        logging.info(f"Validated Data: {validated}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Step 4: Save to Database
    try:
        row_id = save_invoice_to_db(validated)
        logging.info(f"Saved invoice to DB (ID: {row_id})")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # Step 5: Push to ERPNext
    try:
        erp_resp = push_to_erp(validated)
        logging.info(f"ERP Push Response: {erp_resp}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERP push failed: {e}")

    # Step 6: Return Final Response
    return {
        "status": "success",
        "data": validated,
        "db_id": row_id,
        "erp_response": erp_resp
    }
