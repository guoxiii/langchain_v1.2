# ch17/debug_tool_error.py
"""執行會發生錯誤，這是故意的"""
"""製造工具錯誤，練習除錯"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

@tool
def divide(a: float, b: float) -> str:
    """將 a 除以 b，回傳計算結果。"""
    if b == 0:
        raise ValueError("除數不能為零！")
    return str(a / b)

llm = init_chat_model("google_genai:gemini-2.5-flash")

agent = create_agent(
    model=llm,
    tools=[divide],
    system_prompt="你是一個數學計算助手。當工具發生錯誤時，請向使用者說明原因。"
)

# 這會觸發除以零的錯誤
result = agent.invoke(
    {"messages": [{"role": "user", "content": "請幫我計算 10 除以 0"}]}
)

for msg in result["messages"]:
    print(f"[{msg.type}] {msg.text[:200]}")
