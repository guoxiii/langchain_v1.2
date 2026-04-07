"""
檔案：token_saving_demo.py
使用 SummarizationMiddleware 控制對話歷史長度
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import tool

@tool
def get_order_status(order_id: str) -> str:
    """查詢訂單狀態"""
    return f"訂單 {order_id} 狀態：已出貨，預計明天送達"

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_order_status],
    system_prompt="你是電商客服 Agent，用繁體中文回答。",
    middleware=[
        SummarizationMiddleware(
            # 使用便宜的小模型來做摘要（節省成本）
            model="google_genai:gemini-2.5-flash",
            # 觸發條件：任一條件滿足就摘要
            trigger=[
                ("tokens", 4000),    # Token 數超過 4000
                ("messages", 20),    # 訊息數超過 20
            ],
            # 保留最近的部分
            keep=("messages", 6),    # 保留最近 6 則訊息
            summary_prefix="[先前對話摘要] ",
        ),
    ],
)
