import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def llm(prompt: str, temperature: float = 0.0)->str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=temperature,
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao chamar a API da OpenAI: {e}") from e

    content = response.choices[0].message.content.strip()

    # Fallback de segurança: caso o modelo ignore a instrução
    # e devolva o SQL dentro de um bloco markdown
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("sql\n", "", 1).strip()

    return content
