"""
hello_agent.py
第一個 Agent 預覽 — create_agent 初體驗
Agent 能使用工具（Tools）來完成任務。
"""
import os

from dotenv import load_dotenv
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ 錯誤：請在 .env 檔案中設定 GOOGLE_API_KEY")
    exit(1)

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool

# 定義一個簡單的工具：加法計算器
@tool
def add(a: float, b: float) -> float:
    """將兩個數字相加。"""
    return a + b

# 建立模型
model = init_chat_model("google_genai:gemini-2.5-flash")

# 建立 Agent（帶有工具的 AI 助手）
agent = create_agent(
    model=model,
    tools=[add],
    system_prompt="你是一個有用的助手，可以幫忙做數學計算。",
)

# 讓 Agent 回答問題
result = agent.invoke(
    {"messages": [{"role": "user", "content": "請幫我計算 123.45 + 678.90 等於多少？"}]}
)

# 印出 Agent 的最終回應
for message in result["messages"]:
    if hasattr(message, "content") and message.content:
        print(f"[{message.type}] {message.content}")
