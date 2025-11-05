# backend/llm_extractor.py
import re

def extract_fields(text: str) -> dict:
    """
    Extract fields like invoice number, date, and total
    from receipts and invoices.
    Works for formats like:
      - BILL NO / TOKEN NO
      - DD-MM-YYYY
      - NET TOTAL / TOTAL / AMOUNT / GRAND TOTAL
    """

    clean_text = text.replace("\n", " ").replace("\r", " ").strip().upper()
    print(" Cleaned OCR Text:", clean_text[:300])  

    # Invoice / Bill / Token Number
    invoice_number = re.search(
        r"(?:BILL\s*NO|INVOICE\s*NO|INVOICE NUMBER\s*No|TOKEN\s*NO|RECEIPT\s*NO)\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        clean_text
    )

    #  Date (DD-MM-YYYY or DD/MM/YYYY)
    invoice_date = re.search(
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        clean_text
    )

    # Total amount — handles “NET TOTAL 80.00”, “TOTAL: 80”, etc.
    total_amount = re.search(
        r"(?:NET\s*TOTAL|GRAND\s*TOTAL|TOTAL|AMOUNT\s*DUE|BALANCE\s*DUE|SUB\s*TOTAL)\s*[:\-]?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        clean_text
    )

    #  Vendor Name (optional improvement)
    vendor_match = re.search(
        r"([A-Z\s]+(?:HOTEL|RESTAURANT|CAFE|STORE|SHOP|MART)[A-Z\s]*)",
        clean_text
    )
    vendor_name = vendor_match.group(1).strip() if vendor_match else "Unknown Vendor"

    fields = {
        "invoice_number": invoice_number.group(1) if invoice_number else None,
        "invoice_date": invoice_date.group(1) if invoice_date else None,
        "total": total_amount.group(1) if total_amount else None,
        "vendor_name": vendor_name,
    }

    print("Extracted fields:", fields)
    return fields






#-------------------------------working llm code --------------------------------

# backend/llm_extractor.py
# import os
# import json
# import re
# import requests

# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# def extract_fields(text: str) -> dict:
#     """
#     Use Groq Llama 3.3-70b model to extract invoice data directly.
#     Returns: dict with invoice_number, invoice_date, total, vendor_name
#     """
#     print("Raw OCR Text:", text[:300])

#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": (
#                     "You are an invoice information extractor. "
#                     "Extract and return ONLY JSON in this exact format:\n"
#                     "{\n"
#                     "  \"invoice_number\": string,\n"
#                     "  \"invoice_date\": string,\n"
#                     "  \"total\": number,\n"
#                     "  \"vendor_name\": string\n"
#                     "}"
#                 )
#             },
#             {"role": "user", "content": text}
#         ],
#         "temperature": 0.1
#     }

#     try:
#         response = requests.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers=headers,
#             json=payload,
#             timeout=30
#         )
#         response.raise_for_status()
#         result = response.json()
#         ai_output = result["choices"][0]["message"]["content"]

#         # Clean possible ```json code fences
#         cleaned_output = re.sub(r"```(json)?", "", ai_output).strip("` \n")
#         data = json.loads(cleaned_output)
#         print("Extracted with LLM:", data)
#         return data

#     except Exception as e:
#         print(f" LLM extraction failed: {e}")
#         return {
#             "invoice_number": None,
#             "invoice_date": None,
#             "total": None,
#             "vendor_name": "Unknown"
#         }
