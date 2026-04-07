"""
檔案：langsmith_monitoring_demo.py
透過 LangSmith SDK 設定自訂追蹤與標籤
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langsmith import traceable

@tool
def search_faq(query: str) -> str:
    """搜尋 FAQ"""
    return "找到相關 FAQ 條目..."

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[search_faq],
    system_prompt="你是客服 Agent。",
)

@traceable(
    run_type="chain",
    name="customer_service_interaction",
    tags=["production", "customer-service"],
    metadata={"version": "1.2.0", "region": "asia-east1"},
)

async def handle_customer_query(
    user_id: str,
    query: str,
    tier: str = "free",
):
    """
    處理客戶查詢的入口函式。
    @traceable 裝飾器會自動將執行過程上報到 LangSmith，
    包括 tags 和 metadata，方便後續篩選和分析。
    """
    config = {
        "run_name": f"customer_query_{tier}",
        "tags": [f"tier:{tier}", f"user:{user_id}"],
        "metadata": {
            "user_id": user_id,
            "user_tier": tier,
        },
    }

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
    )

    return result
