import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH")
def execute_sql(sql: str)-> list[dict]:
    uri_ro = f"file:{DB_PATH}?mode=ro"
    connection = sqlite3.connect(uri_ro, uri=True)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)

        cols = [descricao[0] for descricao in cursor.description]
        rows = cursor.fetchall()

        result = [dict(zip(cols, row)) for row in rows]
        return result
    except sqlite3.OperationalError as e:
        print(f"Operation Denied: {e}")
    finally:
        connection.close()
