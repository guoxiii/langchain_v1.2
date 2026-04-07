# src/order_agent.py

"""
整合 MCP 訂單系統的 Agent
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_order_query_agent():
    """建立整合訂單查詢 MCP 的 Agent"""
    # 連接 MCP Server
    client = MultiServerMCPClient(
        {
            "order-system": {
                "command": "uv",
                "args": ["run", "src/order_mcp_server.py"],
                "transport": "stdio",
            }
        }
    )

    # 從 MCP Server 載入工具
    mcp_tools = await client.get_tools()
    print(f"✅ 已連接 MCP Server，載入 {len(mcp_tools)} 個工具：")

    for tool in mcp_tools:
        print(f"   - {tool.name}: {tool.description[:50]}...")

    # 建立 Agent
    agent = create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=mcp_tools,
        system_prompt="""你是電商客服助理，負責幫顧客查詢訂單狀態、追蹤物流、處理退貨申請。

查詢訂單時的規則：
1. 如果顧客提供訂單編號，直接用 query_order_by_id 查詢
2. 如果顧客提供顧客編號或身份資訊，用 query_orders_by_customer 查詢
3. 如果顧客想追蹤物流，使用 track_shipment 工具
4. 退貨申請需要顧客確認後再提交

回覆風格：
- 簡潔明瞭，直接告訴顧客他們想知道的
- 如果有物流資訊，主動提供最新的配送狀態
- 對等待中的顧客表示理解和感謝
""",
    )

    # 測試對話
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "我想查一下訂單 ORD-202501-001 的狀態，東西到哪了？",
                }
            ]
        }
    )

    last_message = result["messages"][-1]
    print(f"\n🤖 客服助理：{last_message.content}")


if __name__ == "__main__":
    asyncio.run(create_order_query_agent())