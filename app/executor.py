import sqlite3

class ExecuteSQLError(Exception):
    pass

def execute_sql(db_path: str, sql: str)-> list[dict]:
    uri_ro = f"file:{db_path}?mode=ro"
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
