import sqlite3 

# connect to the datacabse 
conn  = sqlite3.connect('invoices.db')
cursor  =conn.cursor()

# check if the invoices table exists
cursor.execute("""
    SELECT name FROM sqlite_master WHERE type='table';
""")
print(cursor.fetchall())

#read data from one table
cursor.execute("SELECT * FROM invoices;")
for row in cursor.fetchall():
    print(row)

