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
def validate_invoice_data(data):
    """
    Validate and normalize extracted invoice data.
    Ensures numeric values and computes total automatically.
    """

    # Default invoice number
    if not data.get("invoice_number"):
        data["invoice_number"] = "UNKNOWN"

    # Ensure items exist
    items = data.get("items", [])
    valid_items = []
    total_amount = 0.0

    for item in items:
        try:
            qty = float(str(item.get("quantity", 1)).replace(",", "").strip())
            rate = float(str(item.get("rate", 0)).replace(",", "").strip())
            desc = item.get("description", "Unknown Item")

            total_amount += qty * rate

            valid_items.append({
                "description": desc,
                "quantity": qty,
                "rate": rate
            })
        except Exception:
            continue

    data["items"] = valid_items
    data["total"] = round(total_amount, 2)  # calculate total

    # Fallback if total not valid
    if not isinstance(data["total"], (int, float)):
        data["total"] = 0.0

    return data
