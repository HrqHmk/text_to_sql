# Text-to-SQL ERP

Um assistente que traduz perguntas em português para consultas SQL sobre uma base
de dados (fornecedores, pedidos de compra, produtos e notas fiscais), executa
a consulta com segurança e devolve a resposta em linguagem natural.

Projeto de portfólio construído para explorar aplicação de LLMs em processos de
negócio (compras, fiscal, financeiro) — um domínio diferente de RAG/atendimento ao
cliente, mas usando boa parte da mesma disciplina de engenharia: validação de
entrada, camadas de segurança, e separação clara de responsabilidades.

## Como funciona

```
pergunta do usuário (texto em português)
        ↓
schema.py       → descreve as tabelas do banco em texto, direto do SQLite
        ↓
prompts.py      → monta o prompt (schema + exemplos few-shot + pergunta)
        ↓
llm.py          → chama a API da OpenAI, recebe o SQL gerado
        ↓
validador.py    → analisa a árvore sintática do SQL (via sqlglot) e bloqueia
                  qualquer coisa que não seja um SELECT seguro
        ↓
executor.py     → executa o SQL validado em uma conexão SQLite somente leitura
        ↓
llm.py (de novo)→ transforma o resultado bruto em uma resposta em português claro
        ↓
interface.py    → Gradio: mostra a pergunta, o SQL gerado, a tabela e a resposta
```

## Por que validar o SQL antes de executar

Instruir o modelo a "gerar apenas SELECT" no prompt é necessário, mas não é
suficiente — é uma sugestão, não uma garantia. Por isso o projeto tem uma camada
separada (`validador.py`) que:

- Faz o parsing do SQL gerado em uma árvore sintática real (com [sqlglot](https://github.com/tobymao/sqlglot), não regex)
- Rejeita qualquer instrução que não seja `SELECT` (ou `WITH ... SELECT`)
- Bloqueia múltiplas instruções na mesma query (ex: `SELECT ...; DELETE ...`)
- Recusa comandos como `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `ATTACH`, `PRAGMA`

Como segunda camada de defesa, o `executor.py` abre a conexão com o SQLite em modo
**somente leitura** (`mode=ro`), então mesmo que o validador falhasse, o banco
recusaria fisicamente qualquer escrita.

## Estrutura do projeto

```
text-to-sql-erp/
├── data/
│   ├── gerar_base_erp.py   # gera a base sintética com Faker (reprodutível, seed fixa)
│   └── database.db              # banco SQLite gerado
├── app/
│   ├── schema.py           # lê o SQLite e descreve as tabelas em texto
│   ├── prompts.py          # prompt few-shot + prompt de resposta em linguagem natural
│   ├── llm.py               # chamada à API da OpenAI
│   ├── validador.py         # validação do SQL via AST (sqlglot)
│   ├── executor.py          # execução do SQL em modo somente leitura
│   └── pipeline.py          # orquestra o fluxo completo, ponta a ponta
├── interface.py              # interface Gradio (camada fina, sem lógica de negócio)
├── requirements.txt
├── .env.example
└── README.md
```

## Base de dados

Os dados são **100% sintéticos**, gerados com [Faker](https://faker.readthedocs.io/)
(`pt_BR`) e seed fixa, o que torna a base reprodutível. O gerador simula regras de
negócio simples para dar realismo às consultas:

- ~65% dos pedidos entregues no prazo, ~25% atrasados, restante pendente ou cancelado
- Notas fiscais só existem para pedidos não cancelados
- Status de pagamento calculado a partir da data de vencimento

Para regenerar a base:
```bash
cd data
python3 gerar_base_erp.py
```

## Como rodar

```bash
git clone <repo>
cd text-to-sql-erp
pip install -r requirements.txt
cp .env.example .env
# edite o .env e adicione sua OPENAI_API_KEY
python3 interface.py
```

Acesse `http://localhost:7860`. Exemplos de perguntas já vêm carregados na interface.

## Exemplos de perguntas

- "Quais são os 5 fornecedores com maior atraso médio de entrega?"
- "Quais notas fiscais estão em aberto e vencem nos próximos 7 dias?"
- "Qual o valor total de pedidos por categoria de produto?"
- "Quantos pedidos foram cancelados no último mês?"

## Limitações conhecidas

- Validação de SQL cobre os principais vetores de risco (múltiplas instruções,
  comandos de escrita), mas não substitui um ambiente de banco com permissões
  de usuário isoladas em produção real.
- O modelo pode gerar consultas incorretas para perguntas muito ambíguas ou fora
  do domínio das 4 tabelas existentes — nesses casos, é instruído a responder
  com um erro explícito em vez de alucinar uma tabela/coluna inexistente.
- Não há memória de conversa entre perguntas (cada pergunta é tratada de forma
  independente).

## Possíveis próximos passos

- Suporte a follow-up ("e desses, quantos são de São Paulo?") com contexto da
  pergunta anterior
- Rodar com um modelo local via Ollama, comparando qualidade de SQL gerado
- Testes automatizados cobrindo o validador com casos adversariais