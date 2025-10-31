# backend/db.py
import sqlite3
from typing import Dict
import os

DB_NAME = os.getenv("INVOICE_DB", "invoices.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT,
    vendor_name TEXT,
    date TEXT,
    total REAL
)
"""

def save_invoice_to_db(data: Dict) -> int:
    with sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(
            "INSERT INTO invoices (invoice_number, vendor_name, date, total) VALUES (?, ?, ?, ?)",
            (data.get("invoice_number"), data.get("vendor_name"), data.get("date"), data.get("total")),
        )
        return cursor.lastrowid
