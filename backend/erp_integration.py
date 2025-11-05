# # backend/erp_integration.py
# import os
# import requests
# from dotenv import load_dotenv
# from backend.zoho_auth import get_zoho_access_token

# # Load environment variables
# load_dotenv()

# def push_to_erp(data: dict) -> dict:
#     """
#     Push validated invoice data to Zoho Books via REST API.
#     Automatically refreshes access token and retries if one endpoint fails.
#     """

#     ZOHO_ORG_ID = os.getenv("ZOHO_ORG_ID", "60057165181")

#     #  Get Zoho OAuth token dynamically
#     token = get_zoho_access_token()
#     if not token:
#         return {"status": "error", "message": "Zoho OAuth token fetch failed."}

#     #  Endpoints
#     primary_url = "https://www.zohoapis.in/books/v3/invoices"  
#     backup_url = "https://books.zoho.in/api/v3/invoices"

#     #  Build invoice payload
#     payload = {
#         "customer_name": data.get("vendor_name", "Walk-In Customer"),
#         "reference_number": data.get("invoice_number", "N/A"),
#         "date": data.get("invoice_date"),
#         "line_items": [
#             {
#                 "description": f"Auto-generated invoice for {data.get('vendor_name', 'Unknown')}",
#                 "name": f"Invoice {data.get('invoice_number', 'N/A')}",
#                 "quantity": 1,
#                 "rate": float(data.get("total", 0.0))
#             }
#         ]
#     }

#     headers = {
#         "Authorization": f"Zoho-oauthtoken {token}",
#         "X-com-zoho-books-organizationid": ZOHO_ORG_ID,
#         "Content-Type": "application/json"
#     }

#     # Try primary domain
#     try:
#         resp = requests.post(primary_url, json=payload, headers=headers, timeout=30)
#         resp.raise_for_status()

#         result = resp.json()
#         return {
#             "status": "success",
#             "invoice_id": result.get("invoice", {}).get("invoice_id"),
#             "invoice_number": result.get("invoice", {}).get("invoice_number"),
#             "invoice_url": result.get("invoice", {}).get("invoice_url"),
#             "message": f" Invoice pushed successfully to Zoho Books ({primary_url})"
#         }

#     except requests.exceptions.RequestException as e:
#         print(f" Primary domain failed: {e}")
#         print("Retrying with alternate domain...")

#         try:
#             resp = requests.post(backup_url, json=payload, headers=headers, timeout=60)
#             resp.raise_for_status()

#             result = resp.json()
#             return {
#                 "status": "success",
#                 "invoice_id": result.get("invoice", {}).get("invoice_id"),
#                 "invoice_number": result.get("invoice", {}).get("invoice_number"),
#                 "invoice_url": result.get("invoice", {}).get("invoice_url"),
#                 "message": f" Invoice pushed successfully to Zoho Books ({backup_url})"
#             }

#         except requests.exceptions.RequestException as e2:
#             return {
#                 "status": "error",
#                 "message": f" Both Zoho API endpoints failed. Error: {e2}"
#             }

#     except Exception as e:
#         return {"status": "error", "message": f"Unexpected error: {e}"}




import os
import requests
import logging
from backend.zoho_auth import get_zoho_access_token

# -------------------- CONFIG --------------------
ZOHO_ORG_ID = os.getenv("ZOHO_ORG_ID", "60057165181")
BASE_URL = "https://www.zohoapis.in/books/v3"


# -------------------- HELPERS --------------------
def get_headers():
    """Return valid Zoho Books headers with fresh OAuth token."""
    token = get_zoho_access_token()
    if not token:
        raise ValueError(" Zoho access token fetch failed.")
    
    return {
        "Authorization": f"Zoho-oauthtoken {token.strip()}",
        "X-com-zoho-books-organizationid": ZOHO_ORG_ID,
        "Content-Type": "application/json"
    }


def get_customer_id(customer_name: str):
    """Check if customer already exists in Zoho Books."""
    url = f"{BASE_URL}/contacts?organization_id={ZOHO_ORG_ID}"
    headers = get_headers()

    resp = requests.get(url, headers=headers, timeout=30)
    if not resp.ok:
        logging.error(f" Failed to fetch customers: {resp.text}")
        return None

    contacts = resp.json().get("contacts", [])
    for c in contacts:
        if c["contact_name"].lower() == customer_name.lower():
            return c["contact_id"]
    return None


def create_customer(customer_name: str, email: str = "auto@system.com"):
    """Create a new customer in Zoho Books."""
    url = f"{BASE_URL}/contacts?organization_id={ZOHO_ORG_ID}"
    headers = get_headers()

    payload = {
        "contact_name": customer_name,
        "email": email,
        "billing_address": {"address": "Auto-created by OCR Agent"}
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    data = resp.json()
    
    if resp.ok:
        logging.info(f" Created new customer: {customer_name}")
        return data.get("contact", {}).get("contact_id")
    else:
        logging.error(f"Customer creation failed: {data}")
        return None


def create_invoice(customer_id: str, reference_number: str, date: str, items: list):
    """Create invoice in Zoho Books with proper item mapping."""
    url = f"{BASE_URL}/invoices?organization_id={ZOHO_ORG_ID}"
    headers = get_headers()

    #  Format line_items for Zoho Books
    formatted_items = []
    for item in items:
        formatted_items.append({
            "item_name": item.get("item_name") or item.get("description") or "Auto Item",
            "description": item.get("description", ""),
            "quantity": float(item.get("quantity", 1)),
            "rate": float(item.get("rate", 0))
        })

    # Fallback if somehow empty
    if not formatted_items:
        formatted_items = [{
            "item_name": "Auto Imported Item",
            "description": "No item details found",
            "quantity": 1,
            "rate": 0
        }]

    payload = {
        "customer_id": customer_id,
        "reference_number": reference_number,
        "date": date,
        "line_items": formatted_items
    }

    logging.info(" ERP Payload:\n" + str(payload))

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    data = resp.json()

    if resp.ok:
        invoice = data.get("invoice", {})
        logging.info(f"Invoice created successfully: {invoice.get('invoice_number')}")
        return {
            "status": "success",
            "invoice_id": invoice.get("invoice_id"),
            "invoice_number": invoice.get("invoice_number"),
            "invoice_url": invoice.get("invoice_url"),
            "message": "Invoice pushed successfully to Zoho Books"
        }
    else:
        logging.error(f" Invoice creation failed: {data}")
        return {"status": "error", "message": data.get("message", "Unknown error")}


# -------------------- MAIN FUNCTION --------------------
def push_to_erp(data: dict):
    """
    Full flow:
      1. Get or create customer
      2. Create invoice
    """
    try:
        customer_name = data.get("customer_name", "Walk-In Customer")
        email = data.get("email", "auto@system.com")
        reference_number = data.get("reference_number", "N/A")
        invoice_date = data.get("invoice_date")
        items = data.get("items", [])  # FIXED — correct key!

        # Normalize item fields for Zoho
        normalized_items = []
        for item in items:
            description = item.get("description", "").strip()
            rate = float(item.get("rate", 0))
            quantity = float(item.get("quantity", 1))
            if not description:
                description = "Auto Imported Item"
            normalized_items.append({
                "item_name": description,
                "description": description,
                "quantity": quantity,
                "rate": rate
            })

        # Auto-calculate total for reference (not required by Zoho)
        data["total"] = sum(i["quantity"] * i["rate"] for i in normalized_items)

        # Step 1: Find or create customer
        customer_id = get_customer_id(customer_name)
        if not customer_id:
            logging.info(f" Creating new customer: {customer_name}")
            customer_id = create_customer(customer_name, email)
        else:
            logging.info(f" Found existing customer: {customer_name}")

        if not customer_id:
            return {"status": "error", "message": "Failed to find or create customer"}

        # Step 2: Create invoice
        logging.info(f" Final Invoice Items: {normalized_items}")
        logging.info(f" ERP Payload: {{'customer_id': '{customer_id}', 'reference_number': '{reference_number}', 'date': '{invoice_date}', 'line_items': {normalized_items}}}")

        return create_invoice(customer_id, reference_number, invoice_date, normalized_items)

    except Exception as e:
        logging.exception(" ERP push failed:")
        return {"status": "error", "message": str(e)}
