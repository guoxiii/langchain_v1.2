# 檔案：ch05/hook_order.py

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    before_agent, after_agent,
    before_model, after_model,
    wrap_model_call, wrap_tool_call,
)
from langchain_core.tools import tool

load_dotenv()

# --- 定義工具 ---
@tool
def add(a: int, b: int) -> int:
    """將兩個數字相加"""
    print(f"  🔧 [工具執行] add({a}, {b})")
    return a + b

# --- 定義各個 Hook ---
@before_agent
def hook_before_agent(state, runtime):
    print("1️⃣ [before_agent] Agent 開始")
    return None

@before_model
def hook_before_model(state, runtime):
    print("  3️⃣ [before_model] 模型呼叫前")
    return None

@after_model
def hook_after_model(state, runtime):
    print("  5️⃣ [after_model] 模型回覆後")
    return None

@wrap_model_call
def hook_wrap_model(request, handler):
    print("  4️⃣ [wrap_model_call] 包裹模型呼叫 - 開始")
    result = handler(request)  # 呼叫實際的模型
    print("  4️⃣ [wrap_model_call] 包裹模型呼叫 - 結束")
    return result

@wrap_tool_call
def hook_wrap_tool(request, handler):
    print("  6️⃣ [wrap_tool_call] 包裹工具呼叫 - 開始")
    result = handler(request)  # 呼叫實際的工具
    print("  6️⃣ [wrap_tool_call] 包裹工具呼叫 - 結束")
    return result

@after_agent
def hook_after_agent(state, runtime):
    print("7️⃣ [after_agent] Agent 結束")
    return None

# --- 建立 Agent ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[add],
    middleware=[
        hook_before_agent,
        hook_before_model,
        hook_wrap_model,
        hook_after_model,
        hook_wrap_tool,
        hook_after_agent,
    ],
)

# --- 執行 ---
result = agent.invoke(
    {"messages": [{"role": "user", "content": "請幫我計算 15 + 27"}]}
)

print(f"\n🤖 最終回覆：{result['messages'][-1].content}")
