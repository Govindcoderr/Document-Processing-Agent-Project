# # backend/data_validator.py

def validate_invoice_data(data):
    """
    Validate and normalize extracted invoice data.
    Converts fields, ensures valid line_items for ERP.
    """

    # Default invoice number
    data["invoice_number"] = data.get("invoice_number") or "UNKNOWN"

    # Normalize and validate items
    items = data.get("items", [])
    valid_items = []
    total_amount = 0.0

    for item in items:
        try:
            qty = float(str(item.get("quantity", 1)).replace(",", "").strip())
            rate = float(str(item.get("rate", 0)).replace(",", "").strip())
            desc = item.get("description", "Unknown Item").strip()

            valid_items.append({
                "description": desc,
                "quantity": qty,
                "rate": rate
            })

            total_amount += qty * rate
        except Exception:
            continue

    #  Zoho (ERP) auto-calculates total, so just store it for reference
    data["total"] = round(total_amount, 2)
    data["line_items"] = valid_items   #  ERP expects this field name

    # Remove old key to avoid confusion
    data.pop("items", None)

    return data
