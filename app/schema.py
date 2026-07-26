import os
import sqlite3

def get_schema_description(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]

    schema_description = ""

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        collumns = cursor.fetchall()
        schema_description += f"\nTabela {table}:\n"
        for col in collumns:
            column_name, column_type = col[1], col[2]
            schema_description += f"  - {column_name} ({column_type})\n"

    conn.close()
    return schema_description
