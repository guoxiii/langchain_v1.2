# src/main.py

"""
⚠️ 本範例的權限控制僅透過 System Prompt 實現，屬於展示用途。
生產環境中，敏感功能應搭配真正的身份驗證機制（如 JWT Token、API Key、或登入系統），
在工具層或 middleware 層做硬性的權限檢查，而非依賴 LLM 的判斷。
"""

"""
電商智能助理 — 主程式入口
整合所有模組的統一 Agent
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from src.product_knowledge import get_vector_store
from src.product_graph import ProductGraphBuilder
from src.multilingual import MultilingualMiddleware, MergeableChat

# ============================================================
# 導入工具（從各模組重新整合）
# ============================================================

from src.recommendation import (
    search_products_by_description,
    get_related_products,
    get_skincare_routine,
    get_products_by_skin_type,
    check_product_stock,
)

@tool
def analyze_sales_with_deep_agent(question: str) -> str:
    """
    使用 Deep Agent 進行銷售數據分析。
    適合需要多步驟分析的複雜數據問題。    

    Args:
        question: 要分析的問題，例如「哪個通路的營收最高？」    

    Returns:
        分析結果
    """

    from src.sales_analysis import create_sales_analysis_agent

    agent = create_sales_analysis_agent()

    result = agent.invoke({
        "messages": [{"role": "user", "content": question}]
    })

    return result["messages"][-1].content

# ============================================================
# 主控 Agent
# ============================================================

async def create_ecommerce_assistant():
    """建立完整的電商智能助理"""
    # 所有本地工具
    local_tools = [
        search_products_by_description,
        get_related_products,
        get_skincare_routine,
        get_products_by_skin_type,
        check_product_stock,
        analyze_sales_with_deep_agent,
    ]

    # 連接 MCP 訂單系統
    mcp_client = MultiServerMCPClient(
        {
            "order-system": {
                "command": "uv",
                "args": ["run", "src/order_mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    mcp_tools = await mcp_client.get_tools()
    all_tools = local_tools + mcp_tools

    print(f"🚀 電商智能助理已啟動！")
    print(f"   已載入 {len(local_tools)} 個本地工具 + {len(mcp_tools)} 個 MCP 工具")

    # 建立主控 Agent — 使用 MergeableChat 自動合併多條 SystemMessage
    agent = create_agent(
        model=MergeableChat(model="claude-sonnet-4-6"),
        tools=all_tools,
        system_prompt="""你是一位全方位的電商智能助理，名叫「小美」。

你可以幫顧客做以下事情：
1. 🛍️ 商品推薦 — 根據膚質、需求推薦適合的保養品
2. 📦 訂單查詢 — 查詢訂單狀態、追蹤物流
3. 📊 銷售分析 — 分析銷售數據、產出報表（僅限內部人員使用）
4. 🔄 退貨申請 — 協助提交退貨/退款申請
5. 🧴 保養諮詢 — 推薦完整的保養流程

對話風格：
- 親切、專業、不囉嗦
- 像朋友一樣聊天，但每句話都有資訊量
- 主動提供額外的有用資訊
- 適時用 emoji 增添親切感

重要規則：
- 商品資訊一定要用工具查詢，不要憑記憶回答
- 訂單資訊一定要用 MCP 工具查詢
- 銷售分析功能只對內部人員開放，如果普通顧客詢問，請禮貌拒絕
- 醫療相關問題請建議顧客諮詢專業醫師
""",
        middleware=[MultilingualMiddleware()],
        checkpointer=MemorySaver(),
    )

    # 互動式對話迴圈
    config = {"configurable": {"thread_id": "session-001"}}
    print("\n💬 開始對話（輸入 'quit' 結束）：\n")

    while True:
        user_input = input("👤 你：")

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("🤖 小美：感謝光臨，祝你有美好的一天！👋")
            break

        # 使用 ainvoke（非同步），MCP 工具是 async-only
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )

        last_message = result["messages"][-1]
        print(f"🤖 小美：{last_message.content}\n")

if __name__ == "__main__":
    asyncio.run(create_ecommerce_assistant())