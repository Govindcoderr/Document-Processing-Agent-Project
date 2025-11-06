import os
import requests
import logging
from datetime import datetime
from backend.zoho_auth import get_zoho_access_token

ZOHO_ORG_ID = os.getenv("ZOHO_ORG_ID", "60057165181")
BASE_URL = "https://www.zohoapis.in/books/v3"

def get_headers():
    token = get_zoho_access_token()
    if not token:
        raise ValueError("Zoho access token fetch failed.")
    return {
        "Authorization": f"Zoho-oauthtoken {token.strip()}",
        "X-com-zoho-books-organizationid": ZOHO_ORG_ID,
        "Content-Type": "application/json"
    }

def get_customer_id(customer_name: str):
    url = f"{BASE_URL}/contacts?organization_id={ZOHO_ORG_ID}"
    resp = requests.get(url, headers=get_headers(), timeout=30)
    if not resp.ok:
        logging.error(f" Failed to fetch customers: {resp.text}")
        return None
    for c in resp.json().get("contacts", []):
        if c["contact_name"].lower() == customer_name.lower():
            return c["contact_id"]
    logging.warning(f" Customer not found: {customer_name}")
    return None

def create_customer(customer_name: str, email="auto@system.com"):
    url = f"{BASE_URL}/contacts?organization_id={ZOHO_ORG_ID}"
    payload = {
        "contact_name": customer_name,
        "email": email,
        "billing_address": {"address": "Auto-created by OCR Agent"}
    }
    resp = requests.post(url, headers=get_headers(), json=payload, timeout=30)
    if resp.ok:
        contact_id = resp.json().get("contact", {}).get("contact_id")
        logging.info(f" Created new customer: {customer_name}")
        return contact_id
    logging.error(f" Customer creation failed: {resp.text}")
    return None

def create_invoice(customer_id: str, reference_number: str, date: str, items: list):
    """Send invoice to Zoho ERP with correct format."""
    if not items:
        logging.error(" No valid line items found for ERP push.")
        return {"status": "error", "message": "No valid items to create invoice."}

    payload = {
        "customer_id": customer_id,
        "reference_number": reference_number or f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": date or datetime.today().strftime("%Y-%m-%d"),
        "line_items": [
            {
                "description": item.get("description", "Auto Imported Item"),
                "quantity": float(item.get("quantity", 1)),
                "rate": float(item.get("rate", 0))
            }
            for item in items
        ],
        "notes": "Auto-created via Document Processing Agent"
    }

    logging.info(f" ERP Payload: {payload}")
    resp = requests.post(f"{BASE_URL}/invoices?organization_id={ZOHO_ORG_ID}",
                         headers=get_headers(), json=payload, timeout=30)
    data = resp.json()
    if resp.ok:
        logging.info(f" Invoice created: {data.get('invoice', {}).get('invoice_number')}")
        return {"status": "success", "message": "Invoice created successfully", "data": data.get("invoice", {})}
    logging.error(f" Invoice creation failed: {data}")
    return {"status": "error", "message": data.get("message", "Unknown error")}

def push_to_erp(data: dict):
    """End-to-end flow: find/create customer → send invoice."""
    try:
        customer_name = data.get("customer_name", "Walk-In Customer")
        email = data.get("email", "auto@system.com")
        ref_no = data.get("reference_number", "N/A")
        date = data.get("invoice_date", datetime.today().strftime("%Y-%m-%d"))
        items = data.get("items") or data.get("line_items", [])

        #  Fallback: if items empty, create one default item
        if not items:
            items = [{
                "description": data.get("description", "Auto Imported Item"),
                "quantity": float(data.get("quantity", 1)),
                "rate": float(data.get("rate", data.get("total", 0)))
            }]

        customer_id = get_customer_id(customer_name)
        if not customer_id:
            logging.info(f"reating new customer: {customer_name}")
            customer_id = create_customer(customer_name, email)

        if not customer_id:
            return {"status": "error", "message": "Failed to create or locate customer"}

        logging.info(f"🧾 Final normalized items: {items}")
        return create_invoice(customer_id, ref_no, date, items)

    except Exception as e:
        logging.exception(" ERP push failed:")
        return {"status": "error", "message": str(e)}
