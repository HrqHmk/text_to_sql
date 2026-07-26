import sqlglot
from sqlglot import exp

PROHIBITED_KEYWORDS = {
    "DROP",
    "INSERT",
    "UPDATE",
    "ALTER",
    "DELETE",
    "CREATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "REPLACE"
}


class SQLInvalidoError(Exception):
    pass

def validate_sql(sql: str) -> str:
    """
    Valida se a consulta SQL é válida e não contém palavras-chave proibidas.
    """
    sql = sql.strip().upper()

    if not sql:
        raise SQLInvalidoError("Empty SQL")

    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as e:
        raise SQLInvalidoError(f"Invalid SQL: {e}") from e

    if len(statements) != 1:
        raise SQLInvalidoError("Only one SQL statement is allowed.")

    statement = statements[0]

    if statement is None:
        raise SQLInvalidoError("The SQL could not be interpreted.")

    root_type = statement.key # ex: 'SELECT', 'INSERT', etc.
    if isinstance(statement, exp.With):
        # CTE: verify if inside in the query has select statement
        body = statement.this
        if not isinstance(body, exp.Select):
            raise SQLInvalidoError("CTEs are only allowed if they end in SELECT.")
    elif not isinstance(statement, exp.Select):
        raise SQLInvalidoError(f"Only SELECT statements are allowed. Found: {root_type.upper()}")

    # Extra check: searches for any prohibited command subexpression
    # (protection against hidden malicious functions/subqueries)
    for node in statement.walk():
        node_obj = node[0] if isinstance(node, tuple) else node
        type_name = type(node_obj).__name__.lower()
        if type_name in PROHIBITED_KEYWORDS:
            raise SQLInvalidoError(f"Prohibited keyword found: {type_name.upper()}")

    return statement.sql(dialect="sqlite")
