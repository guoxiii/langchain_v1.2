"""
檔案：tiered_processing_demo.py
分級處理架構：依據使用者層級與任務複雜度分配資源
"""

from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import (
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.tools import tool

@dataclass
class UserTier:
    """使用者層級設定"""
    name: str
    model: str
    max_tool_calls: int
    max_tokens: int

# 定義不同使用者層級
TIERS = {
    "free": UserTier(
        name="免費版",
        model="google_genai:gemini-2.5-flash",
        max_tool_calls=3,
        max_tokens=500,
    ),
    "pro": UserTier(
        name="專業版",
        model="google_genai:gemini-2.5-flash",
        max_tool_calls=10,
        max_tokens=2000,
    ),
    "enterprise": UserTier(
        name="企業版",
        model="google_genai:gemini-2.5-pro",
        max_tool_calls=25,
        max_tokens=8000,
    ),
}


@tool
def search_knowledge_base(query: str) -> str:
    """搜尋知識庫"""
    return f"找到關於 '{query}' 的相關資訊..."

def create_tiered_agent(user_tier: str):
    """根據使用者層級建立對應的 Agent"""
    tier = TIERS.get(user_tier, TIERS["free"])
    print(f"  🎫 建立 {tier.name} Agent（模型: {tier.model}）")

    return create_agent(
        model=tier.model,
        tools=[search_knowledge_base],
        system_prompt=f"你是 AI 助理。回答長度限制在 {tier.max_tokens} tokens 以內。",
        middleware=[
            ToolCallLimitMiddleware(run_limit=tier.max_tool_calls),
            SummarizationMiddleware(
                model="google_genai:gemini-2.5-flash",
                trigger=[("tokens", 2000)],
                keep=("messages", 4),
            ),
        ],
    )
