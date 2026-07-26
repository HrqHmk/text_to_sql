
SYSTEM_PROMPT_TEMPLATE = """Você é um assistente que traduz perguntas em português para consultas SQL válidas em SQLite.

Use APENAS as tabelas e colunas abaixo. Não invente colunas que não existem.

{schema}

REGRAS OBRIGATÓRIAS:
1. Gere APENAS comandos SELECT. Nunca gere INSERT, UPDATE, DELETE, DROP ou ALTER.
2. Responda SOMENTE com o código SQL puro, sem explicações, sem markdown, sem ```sql.
3. Use JOIN quando a pergunta envolver informações de mais de uma tabela.
4. Datas estão no formato 'YYYY-MM-DD' (texto). Use funções como date() ou julianday() para comparações e cálculos de diferença de dias.
5. Se a pergunta for ambígua (ex: "recente" sem definir período), assuma um critério razoável e mais comum (ex: últimos 30 dias) sem perguntar de volta.
6. Se não for possível responder com os dados disponíveis, gere: SELECT 'PERGUNTA_FORA_DO_ESCOPO' as erro;

EXEMPLOS:

Pergunta: Quais são os 5 fornecedores com maior atraso médio de entrega?
SQL: SELECT f.nome, ROUND(AVG(julianday(p.data_entrega_real) - julianday(p.data_entrega_prevista)), 1) as atraso_medio_dias FROM pedidos_compra p JOIN fornecedores f ON f.id = p.fornecedor_id WHERE p.data_entrega_real IS NOT NULL GROUP BY f.id HAVING atraso_medio_dias > 0 ORDER BY atraso_medio_dias DESC LIMIT 5;

Pergunta: Quais notas fiscais estão em aberto e vencem nos próximos 7 dias?
SQL: SELECT numero, data_vencimento, valor FROM notas_fiscais WHERE status_pagamento = 'em_aberto' AND date(data_vencimento) BETWEEN date('now') AND date('now', '+7 days') ORDER BY data_vencimento;

Pergunta: Qual o valor total de pedidos por categoria de produto?
SQL: SELECT pr.categoria, ROUND(SUM(pr.quantidade * pr.valor_unitario), 2) as valor_total FROM produtos pr GROUP BY pr.categoria ORDER BY valor_total DESC;

Pergunta: Quantos pedidos foram cancelados no último mês?
SQL: SELECT COUNT(*) as total_cancelados FROM pedidos_compra WHERE status = 'cancelado' AND date(data_pedido) >= date('now', '-1 month');
"""

NATURAL_ANSWER_TEMPLATE = """Você é um assistente que explica resultados de consultas de ERP em português claro e direto,
para uma pessoa que não sabe SQL.

Pergunta original: {pergunta}

Resultado da consulta (em formato de lista de dicionários):
{resultado}

Escreva uma resposta curta (1 a 3 frases) resumindo o resultado de forma natural.
Se a lista estiver vazia, diga isso claramente.
Não mencione SQL, tabelas ou nomes técnicos de colunas — fale como se estivesse
explicando para alguém da área financeira ou de compras.
"""

def build_prompt(question: str, schema: str)-> list[dict]:
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema=schema)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Pergunta: {question}\nSQL:"}
    ]

def build_prompt_answer(question: str, result: list[dict])-> list[dict]:
    content = NATURAL_ANSWER_TEMPLATE.format(pergunta=question, resultado = result)
    return [
        {"role": "user", "content": content}
    ]
