from app.schema import get_schema_description
from app.validator import validate_sql
from app.executor import execute_sql

def main():
    print(execute_sql("SELECT * FROM FORNECEDORES"))

if __name__ == "__main__":
    main()
