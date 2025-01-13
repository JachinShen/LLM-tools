import gradio as gr
import pandas as pd

from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langsmith import traceable
from pydantic import BaseModel, Field


class Account(BaseModel):
    account: str = Field(description="分录名")
    balance: float = Field(description="金额")


class Ledger(BaseModel):
    debit: Account = Field(description="借方账户")
    credit: Account = Field(description="贷方账户")


parser = JsonOutputParser(pydantic_object=Ledger)
chat = ChatZhipuAI(model="glm-4-flash", temperature=0.5)

def ask_llm(user_input):
    prompt = PromptTemplate(
        template="你是一个专业会计师，能够将事件精确转换为借贷记账法的会计分录。请确保每个分录都正确地反映了交易的借方和贷方。\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | chat | parser

    # 获取LLM的响应
    response = chain.invoke({"query": user_input})
    return response


@traceable
def main():
    with gr.Blocks() as blocks:
        # Define the state
        ledger_df = gr.State(pd.DataFrame(columns=["debit_account", "debit_balance", "credit_account", "credit_balance"]))

        # Define the input and output
        user_input = gr.Textbox(label="Enter an event")
        output = gr.Dataframe(label="Accounting Journal Entry")

        # Define the save button
        save_button = gr.Button("Save as Excel")
        file_output = gr.File(label="Download Excel File")


        # Define the Gradio interface
        def process_input(user_input, ledger_df):
            journal_entry = ask_llm(user_input)
            entry_df = pd.DataFrame(
                [
                    {
                        "debit_account": journal_entry["debit"]["account"],
                        "debit_balance": journal_entry["debit"]["balance"],
                        "credit_account": journal_entry["credit"]["account"],
                        "credit_balance": journal_entry["credit"]["balance"],
                    }
                ]
            )

            # 更新 DataFrame
            ledger_df = pd.concat([ledger_df, entry_df], ignore_index=True)

            return ledger_df, ledger_df

        # Define the save function
        def save_Ledger(ledger_df):
            # with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            #     ledger_df.to_excel(tmp.name, index=False)
            #     return tmp.name
            ledger_df.to_excel("ledger.xlsx", index=False)
            return "ledger.xlsx"

        # Define the event handlers
        user_input.submit(fn=process_input, inputs=[user_input, ledger_df], outputs=[ledger_df, output])
        save_button.click(fn=save_Ledger, inputs=[ledger_df], outputs=file_output)

        blocks.launch()


if __name__ == "__main__":
    main()
