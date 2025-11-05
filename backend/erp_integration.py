# backend/erp_integration.py
import os
import requests
from dotenv import load_dotenv
from backend.zoho_auth import get_zoho_access_token

# Load environment variables
load_dotenv()

def push_to_erp(data: dict) -> dict:
    """
    Push validated invoice data to Zoho Books via REST API.
    Automatically refreshes access token and retries if one endpoint fails.
    """

    ZOHO_ORG_ID = os.getenv("ZOHO_ORG_ID", "60057165181")

    # 🔐 Get Zoho OAuth token dynamically
    token = get_zoho_access_token()
    if not token:
        return {"status": "error", "message": "Zoho OAuth token fetch failed."}

    # 🌍 API Endpoints
    primary_url = "https://books.zohoapis.in/api/v3/invoices" 
    backup_url = "https://books.zoho.in/api/v3/invoices"

    # 📦 Build invoice payload
    payload = {
        "customer_name": data.get("vendor_name", "Walk-In Customer"),
        "reference_number": data.get("invoice_number", "N/A"),
        "date": data.get("invoice_date"),
        "line_items": [
            {
                "description": f"Auto-generated invoice for {data.get('vendor_name', 'Unknown')}",
                "name": f"Invoice {data.get('invoice_number', 'N/A')}",
                "quantity": 1,
                "rate": float(data.get("total", 0.0))
            }
        ]
    }

    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "X-com-zoho-books-organizationid": ZOHO_ORG_ID,
        "Content-Type": "application/json"
    }

    # 🚀 Try primary domain
    try:
        resp = requests.post(primary_url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()

        result = resp.json()
        return {
            "status": "success",
            "invoice_id": result.get("invoice", {}).get("invoice_id"),
            "invoice_number": result.get("invoice", {}).get("invoice_number"),
            "invoice_url": result.get("invoice", {}).get("invoice_url"),
            "message": f"✅ Invoice pushed successfully to Zoho Books ({primary_url})"
        }

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Primary domain failed: {e}")
        print("🔁 Retrying with alternate domain...")

        try:
            resp = requests.post(backup_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()

            result = resp.json()
            return {
                "status": "success",
                "invoice_id": result.get("invoice", {}).get("invoice_id"),
                "invoice_number": result.get("invoice", {}).get("invoice_number"),
                "invoice_url": result.get("invoice", {}).get("invoice_url"),
                "message": f"✅ Invoice pushed successfully to Zoho Books ({backup_url})"
            }

        except requests.exceptions.RequestException as e2:
            return {
                "status": "error",
                "message": f"❌ Both Zoho API endpoints failed. Error: {e2}"
            }

    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
