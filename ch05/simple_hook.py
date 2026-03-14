# 檔案：ch05/simple_hook.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import before_model, after_model

load_dotenv()

# --- 定義兩個簡單的 Middleware Hook ---
@before_model
def log_before(state, runtime):
    """在每次模型呼叫前，印出目前的訊息數量"""
    msg_count = len(state["messages"])

    print(f"📥 [before_model] 即將呼叫模型，目前有 {msg_count} 則訊息")
    return None  # 回傳 None 表示不修改狀態

@after_model
def log_after(state, runtime):
    """在每次模型回覆後，印出模型的回覆摘要"""
    last_msg = state["messages"][-1]
    preview = last_msg.content[:80] if last_msg.content else "(無文字內容)"

    print(f"📤 [after_model] 模型回覆：{preview}...")
    return None

# --- 建立 Agent ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[log_before, log_after],
)

# --- 執行 ---
result = agent.invoke(
    {"messages": [{"role": "user", "content": "用一句話解釋什麼是 Middleware"}]}
)

print(f"\n🤖 最終回覆：{result['messages'][-1].content}")
