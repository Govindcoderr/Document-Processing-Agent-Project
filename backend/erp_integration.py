# # backend/erp_integration.py
# import os
# import requests
# from typing import Tuple

# ERP_API_URL = os.getenv("ERP_API_URL", "https://example-erp-system.com/api/invoices")
# ERP_API_KEY = os.getenv("ERP_API_KEY")  # optional

# def push_to_erp(data: dict) -> dict:
#     headers = {"Content-Type": "application/json"}
#     if ERP_API_KEY:
#         headers["Authorization"] = f"Bearer {ERP_API_KEY}"
#     resp = requests.post(ERP_API_URL, json=data, headers=headers, timeout=10)
#     try:
#         resp.raise_for_status()
#         return {"status": "success", "code": resp.status_code, "body": resp.json() if resp.content else {}}
#     except requests.HTTPError as e:
#         return {"status": "error", "code": resp.status_code, "text": resp.text}









# # backend/erp_integration.py
# import os
# import xmlrpc.client
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# def push_to_erp(data: dict) -> dict:
#     """
#     Push validated invoice data to Odoo ERP via XML-RPC API.
#     """

#     # Step 1. Credentials from .env file
#     url = os.getenv("ODOO_URL", "https://vavefx.odoo.com/odoo")
#     db = os.getenv("ODOO_DB", "vavefx")  # your Odoo database name
#     username = os.getenv("ODOO_USERNAME" ,"govindsinghmitcs@gmail.com")
#     password = os.getenv("ODOO_PASSWORD", "Govind@9664")

#     # Step 2. Authenticate user
#     common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
#     uid = common.authenticate(db, username, password, {})

#     if not uid:
#         return {"status": "error", "message": "Odoo Authentication failed. Check credentials."}

#     # Step 3. Create an Object proxy to perform actions
#     models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

#     # Step 4. Prepare invoice data
#     invoice_data = {
#         "move_type": "in_invoice",  # 'out_invoice' for customer invoices
#         "partner_id": 1,  # replace with correct vendor/customer ID
#         "invoice_date": data.get("invoice_date"),
#         "invoice_line_ids": [
#             (0, 0, {
#                 "name": f"Invoice {data.get('invoice_number')}",
#                 "quantity": 1,
#                 "price_unit": data.get("total", 0.0),
#             })
#         ]
#     }

#     # Step 5. Create invoice record in Odoo
#     try:
#         invoice_id = models.execute_kw(
#             db, uid, password,
#             "account.move", "create",
#             [invoice_data]
#         )
#         return {"status": "success", "invoice_id": invoice_id}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}




# backend/erp_integration.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def push_to_erp(data: dict) -> dict:
    """
    Push validated invoice data to ERPNext via REST API.
    """

    ERP_URL = os.getenv("ERP_URL")
    ERP_API_KEY = os.getenv("ERP_API_KEY")
    ERP_API_SECRET = os.getenv("ERP_API_SECRET")

    if not all([ERP_URL, ERP_API_KEY, ERP_API_SECRET]):
        return {"status": "error", "message": "ERPNext credentials missing"}

    headers = {
        "Authorization": f"token {ERP_API_KEY}:{ERP_API_SECRET}",
        "Content-Type": "application/json"
    }

    # Build minimal Sales Invoice payload
    invoice_data = {
        "doctype": "Sales Invoice",
        "customer": data.get("vendor_name", "Walk-In Customer"),
        "posting_date": data.get("invoice_date"),
        "items": [
            {
                "item_name": f"Invoice {data.get('invoice_number', '')}",
                "qty": 1,
                "rate": float(data.get("total", 0.0)),
            }
        ]
    }

    try:
        response = requests.post(
            f"{ERP_URL}/api/resource/Sales%20Invoice",
            json=invoice_data,
            headers=headers,
            timeout=10
        )
        if response.status_code in (200, 201):
            return {
                "status": "success",
                "erp_id": response.json().get("data", {}).get("name"),
                "message": "Invoice pushed to ERPNext"
            }
        else:
            return {
                "status": "error",
                "code": response.status_code,
                "body": response.text
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
