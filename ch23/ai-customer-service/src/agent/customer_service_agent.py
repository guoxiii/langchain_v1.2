# src/agent/customer_service_agent.py

"""
AI 智能客服 Agent — 完整版。
整合所有元件：RAG、MCP、Middleware、Checkpointer。
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from src.agent.system_prompt import CUSTOMER_SERVICE_SYSTEM_PROMPT
from src.agent.tracking import create_tracking_config
from src.tools.faq_search import search_faq
from src.tools.escalation import escalate_to_human
from src.middleware import build_middleware_stack

def create_customer_service_agent():
    """建立並回傳客服 Agent。"""

    # 收集所有工具
    tools = [
        search_faq,           # FAQ 知識庫搜尋
        escalate_to_human,    # 人工轉接
        # MCP 工具（create_ticket 等）會在 async 環境中動態載入
    ]

    # 建立 Middleware Stack
    middleware = build_middleware_stack()

    # 建立 Checkpointer（開發環境用 InMemorySaver）
    checkpointer = InMemorySaver()

    # 組裝 Agent！
    agent = create_agent(
        model="google_genai:gemini-2.5-flash",
        tools=tools,
        system_prompt=CUSTOMER_SERVICE_SYSTEM_PROMPT,
        middleware=middleware,
        checkpointer=checkpointer,
    )

    return agent

# === 互動式測試 ===
def main():
    """本地互動式測試。"""
    agent = create_customer_service_agent()

    print("🤖 AI 智能客服已啟動！輸入 'quit' 結束對話。")
    print("=" * 50)

    thread_id = "test-session-001"

    while True:
        user_input = input("\n👤 客戶：").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 感謝您的使用，再見！")
            break

        config = create_tracking_config(
            thread_id=thread_id,
            customer_id="test-customer",
            channel="terminal",
        )

        result = agent.invoke(
            {"messages": [("user", user_input)]},
            config=config,
        )

        # 取得 Agent 最後的回覆
        last_message = result["messages"][-1]

        if isinstance(last_message.content, str):
            print(f"\n🤖 客服：{last_message.content}")
        else:
            print(f"\n🤖 客服：{last_message.content[0]["text"]}")

if __name__ == "__main__":
    main()
