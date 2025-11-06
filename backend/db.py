
import sqlite3
from typing import Dict
import os

DB_NAME = os.getenv("INVOICE_DB", "invoices.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT,
    customer_name TEXT,
    invoice_date TEXT,
    total REAL
)
"""

def save_invoice_to_db(data: Dict) -> int:
    """
    Saves validated invoice data to local SQLite DB.
    Uses consistent field names with extracted data.
    """
    with sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(
            """
            INSERT INTO invoices (invoice_number, customer_name, invoice_date, total)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.get("invoice_number"),
                data.get("customer_name"),
                data.get("invoice_date"),
                data.get("total", 0.0),
            ),
        )
        conn.commit()
        return cursor.lastrowid
