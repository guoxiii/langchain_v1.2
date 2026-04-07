# src/tools/intent_router.py

"""
意圖識別工具。
使用 Structured Output 將客戶訊息路由到不同的處理流程。
"""

from enum import Enum
from pydantic import BaseModel, Field

class CustomerIntent(str, Enum):
    """客戶意圖分類。"""
    FAQ_QUERY = "faq_query"           # 常見問題查詢
    CREATE_TICKET = "create_ticket"    # 需要建立工單
    ESCALATE = "escalate"              # 需要轉接真人
    GREETING = "greeting"              # 一般問候
    FEEDBACK = "feedback"              # 意見回饋
    ORDER_STATUS = "order_status"      # 訂單狀態查詢

class IntentAnalysis(BaseModel):
    """客戶意圖分析結果。"""
    intent: CustomerIntent = Field(
        description="識別出的客戶意圖分類"
    )

    confidence: float = Field(
        description="意圖識別的信心分數，0.0 到 1.0",
        ge=0.0,
        le=1.0,
    )

    reasoning: str = Field(
        description="判斷此意圖的簡短推理說明"
    )

    requires_human: bool = Field(
        description="是否需要人工介入",
        default=False,
    )

    sentiment: str = Field(
        description="客戶情緒：positive / neutral / negative / angry",
        default="neutral",
    )
