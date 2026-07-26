import os
from dotenv import load_dotenv
from dataclasses import dataclass

from app.schema import get_schema_description
from app.prompts import build_prompt, build_prompt_answer
from app.llm import llm
from app.validator import validate_sql, SQLInvalidoError
from app.executor import execute_sql, ExecuteSQLError

@dataclass
class ResultPipeline:
    question: str
    sql_generated: str
    sql_valid: bool
    error: str | None
    data: list[dict]
    natural_response: str

def answer_question(question: str, db_path: str = None) -> ResultPipeline:
    if not db_path:
        load_dotenv()
        db_path = os.getenv("DB_PATH")

    schema = get_schema_description(db_path)

    prompt_sql = build_prompt(question, schema)
    sql_raw = llm(prompt_sql, temperature=0.0)

    try:
        sql_safe = validate_sql(sql_raw)
    except SQLInvalidoError as e:
        return ResultPipeline(
            question=question,
            sql_generated=sql_raw,
            sql_valid=False,
            error=str(e),
            data=[],
            natural_response="Não consegui gerar uma consulta segura para essa pergunta. Tente reformular."
        )

    try:
        data = execute_sql(db_path, sql_safe)
    except ExecuteSQLError as e:
        return ResultPipeline(
            question=question,
            sql_generated=sql_raw,
            sql_valid=False,
            error=str(e),
            data=[],
            natural_response="A consulta foi gerada mas ocorreram erros ao executá-la no banco."
        )

    if data:
        answer_prompt = build_prompt_answer(question, data)
        natural_response = llm(answer_prompt, temperature=0.3)
    else:
        natural_response = "Não encontrei nenhum registro para esta pergunta."

    return ResultPipeline(
        question=question,
        sql_generated=sql_safe,
        sql_valid=True,
        error=None,
        data=data,
        natural_response=natural_response    
    )
