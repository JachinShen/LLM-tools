import tempfile
import gradio as gr
import pandas as pd

from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
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
system_message = SystemMessagePromptTemplate.from_template(
    "你是一个专业会计师，能够将事件精确转换为借贷记账法的会计分录。请确保每个分录都正确地反映了交易的借方和贷方。")
human_message = HumanMessagePromptTemplate.from_template(
    "历史账目如下：\n{ledger}\n{format_instructions}\n{query}\n",
    input_variables=["query", "ledger"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def ask_llm(user_input, ledger_df):
    # 获取最新的10条账目
    latest_ledger = ledger_df.tail(10)
    ledger_str = latest_ledger.to_string(index=False)
    prompt = ChatPromptTemplate(
        messages = [
            system_message,
            human_message
        ],
    )

    chain = prompt | chat | parser

    # 获取LLM的响应
    response = chain.invoke({"query": user_input, "ledger": ledger_str})
    return response


@traceable
def main():
    with gr.Blocks() as blocks:
        # 定义状态
        ledger_df = gr.State(pd.DataFrame(columns=["debit_account", "debit_balance", "credit_account", "credit_balance"]))

        # 定义输入和输出
        user_input = gr.Textbox(label="输入事件")
        output = gr.Dataframe(label="当前会计分录")

        # 定义文件上传组件
        file_input = gr.File(label="上传历史账目文件(可选，Excel格式)")

        # 定义保存按钮
        save_button = gr.Button("保存为Excel")
        file_output = gr.File(label="下载Excel文件")

        # 定义显示账目的Dataframe组件
        ledger_display = gr.Dataframe(label="历史账目", interactive=False)

        # 定义处理输入的函数
        def process_input(user_input, ledger_df):
            journal_entry = ask_llm(user_input, ledger_df)
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

            # 更新DataFrame
            ledger_df = pd.concat([ledger_df, entry_df], ignore_index=True)

            return ledger_df, entry_df, ledger_df

        # 定义加载Excel文件的函数
        def load_excel(file):
            # 读取Excel文件
            excel_df = pd.read_excel(file.name)
            # 检查列是否匹配
            required_columns = ["debit_account", "debit_balance", "credit_account", "credit_balance"]
            if not all(column in excel_df.columns for column in required_columns):
                raise ValueError("Excel文件必须包含以下列：debit_account, debit_balance, credit_account, credit_balance")
            ledger_df = excel_df
            return ledger_df, ledger_df

        # 定义保存函数
        def save_Ledger(ledger_df):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                ledger_df.to_excel(tmp.name, index=False)
                return tmp.name

        # 定义事件处理
        user_input.submit(fn=process_input, inputs=[user_input, ledger_df], outputs=[ledger_df, output, ledger_display])
        file_input.upload(fn=load_excel, inputs=[file_input], outputs=[ledger_df, ledger_display])
        save_button.click(fn=save_Ledger, inputs=[ledger_df], outputs=file_output)

        blocks.launch()


if __name__ == "__main__":
    main()
