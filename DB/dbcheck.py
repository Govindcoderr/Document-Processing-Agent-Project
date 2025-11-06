# dbcheck.py
import sqlite3
import os

DB_PATH = os.path.abspath("invoices.db")
print(f" Database Path: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for t in tables:
    print(" -", t[0])

print("\n All Invoices:")
cursor.execute("SELECT * FROM invoices;")
rows = cursor.fetchall()
if not rows:
    print(" No data found in invoices table.")
else:
    for row in rows:
        print(row)

conn.close()
