import pandas as pd
import gradio as gr

from app.pipeline import answer_question

EXEMPLOS = [
    "Quais são os 5 fornecedores com maior atraso médio de entrega?",
    "Quais notas fiscais estão em aberto e vencem nos próximos 7 dias?",
    "Qual o valor total de pedidos por categoria de produto?",
    "Quantos pedidos foram cancelados no último mês?",
]


def process_question(question: str):
    if not question or not question.strip():
        return "SELECT 'aguardando pergunta';", pd.DataFrame(), "Digite uma pergunta para começar."

    result = answer_question(question)

    table = pd.DataFrame(result.data) if result.data else pd.DataFrame()

    if result.error:
        sql_shown = f"-- {result.error}\n{result.sql_generated}"
    else:
        sql_shown = result.sql_generated

    return sql_shown, table, result.natural_response


with gr.Blocks(title="Text-to-SQL ERP") as demo:
    gr.Markdown(
        """
        # Consulta em linguagem natural sobre dados de ERP
        Pergunte em português sobre fornecedores, pedidos de compra e notas fiscais.
        O SQL gerado é validado (somente SELECT) antes de ser executado.
        """
    )

    with gr.Row():
        question_input = gr.Textbox(
            label="Sua pergunta",
            placeholder="Ex: Quais fornecedores mais atrasam entregas?",
            scale=4,
        )
        button = gr.Button("Perguntar", variant="primary", scale=1)

    gr.Examples(examples=EXEMPLOS, inputs=question_input)

    answer_output = gr.Textbox(label="Resposta", interactive=False)

    with gr.Accordion("Ver SQL gerado e dados brutos", open=False):
        sql_output = gr.Code(label="SQL gerado", language="sql")
        tabela_output = gr.Dataframe(label="Resultado bruto")

    button.click(
        fn=process_question,
        inputs=question_input,
        outputs=[sql_output, tabela_output, answer_output],
    )
    question_input.submit(
        fn=process_question,
        inputs=question_input,
        outputs=[sql_output, tabela_output, answer_output],
    )

if __name__ == "__main__":
    demo.launch()
