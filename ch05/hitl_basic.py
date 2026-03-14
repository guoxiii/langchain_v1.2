# 檔案：ch05/hitl_basic.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# --- 定義工具 ---
@tool
def read_email(email_id: str) -> str:
    """讀取指定 ID 的 Email 內容"""
    return f"Email #{email_id} 的內容：明天下午三點開會。"

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """發送 Email 給指定收件人"""
    return f"Email 已發送給 {recipient}，主旨：{subject}"

# --- 建立 Agent ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[read_email, send_email],
    checkpointer=InMemorySaver(),  # ⚠️ HITL 必須搭配 Checkpointer
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    "description": "發送 Email 前需要人工審核",
                },
                "read_email": False,  # 讀取 Email 不需要審核
            }
        ),
    ],
)

# --- 執行 ---
thread_config = {"configurable": {"thread_id": "demo-001"}}

# 第一步：使用者提出請求
result = agent.invoke(
    {"messages": [{"role": "user", "content": "幫我寄一封 Email 給 boss@company.com，主旨是「請假申請」，內容是我明天要請假"}]},
    config=thread_config,
)

# 如果有中斷（interrupt），顯示待審核的工具呼叫
if hasattr(result, '__interrupt__') or result.get('__interrupt__'):
    print("⏸️ Agent 已暫停，等待人工審核...")
    print("待審核的操作：發送 Email")
    print("收件人：boss@company.com")
    print("主旨：請假申請")
