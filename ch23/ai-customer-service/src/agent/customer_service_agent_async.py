# src/agent/customer_service_agent_async.py

"""
AI 智能客服 Agent — 非同步版本（含 MCP 工具）。
"""

# ===== Google GenAI SDK 已知問題的暫時處理 =====
# 1. SDK 內部的 AsyncClient.__del__ 會建立未被 await 的協程（Issue #1709）
# 2. Function Calling 的 schema 不支援 additionalProperties 欄位
# 這兩個都是 Google SDK 端的問題，不影響功能，待官方修復後可移除

import asyncio
import logging
import warnings
from dotenv import load_dotenv

load_dotenv()

# Google Gemini API 的 Function Calling（工具調用）目前不支援 additionalProperties 這個欄位
# 隱藏 langchain_google_genai 產生的無害警告，只顯示 ERROR 層級以上的訊息
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
# 隱藏關機時 Google GenAI 底層的協程清理警告  <-- 新增這行
warnings.filterwarnings("ignore", message="coroutine 'BaseApiClient.aclose' was never awaited")

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from src.agent.system_prompt import CUSTOMER_SERVICE_SYSTEM_PROMPT
from src.agent.tracking import create_tracking_config
from src.tools.faq_search import search_faq
from src.tools.escalation import escalate_to_human
from src.middleware import build_middleware_stack

async def run_with_mcp():
    """使用 MCP 工具的非同步版本。"""
    # 建立 MCP Client 並載入工具
    mcp_config = {
        "ticket-system": {
            "command": "uv",
            "args": [
                "run", "python", "-m",
                "src.mcp_servers.ticket_server",
            ],
            "transport": "stdio",
        },
    }

    mcp_client = MultiServerMCPClient(mcp_config)
    mcp_tools = await mcp_client.get_tools()

    all_tools = [
        search_faq,
        escalate_to_human,
        *mcp_tools,  # create_ticket, get_ticket_status, update_ticket
    ]

    # 建立 Agent
    agent = create_agent(
        model="google_genai:gemini-2.5-flash",
        tools=all_tools,
        system_prompt=CUSTOMER_SERVICE_SYSTEM_PROMPT,
        middleware=build_middleware_stack(),
        checkpointer=InMemorySaver(),
    )

    print("🤖 AI 智能客服已啟動（含工單系統）！")
    print("=" * 50)

    thread_id = "test-session-002"

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

        result = await agent.ainvoke(
            {"messages": [("user", user_input)]},
            config=config,
        )

        last_message = result["messages"][-1]

        if isinstance(last_message.content, str):
            print(f"\n🤖 客服：{last_message.content}")
        else:
            print(f"\n🤖 客服：{last_message.content[0]['text']}")

if __name__ == "__main__":
    asyncio.run(run_with_mcp())