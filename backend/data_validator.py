# # backend/data_validator.py

# def validate_invoice_data(data):
#     """
#     Validates extracted invoice data and converts total to float.
#     """
#     if not data.get("invoice_number"):
#         raise ValueError("Missing required field: invoice_number")

#     if not data.get("total"):
#         raise ValueError("Missing required field: total")

#     try:
#         data["total"] = float(str(data["total"]).replace(",", "").strip())
#     except Exception:
#         raise ValueError("Invalid total amount format")

#     return data

#-------------------------------test code -------------------------------

# backend/data_validator.py
def validate_invoice_data(data):
    if not data.get("invoice_number"):
        data["invoice_number"] = "UNKNOWN"

    # 👇 instead of raising, set 0.0
    if not data.get("total"):
        data["total"] = 0.0

    try:
        data["total"] = float(str(data["total"]).replace(",", "").strip())
    except Exception:
        data["total"] = 0.0
    return data
