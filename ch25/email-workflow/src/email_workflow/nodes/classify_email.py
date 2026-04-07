# src/email_workflow/nodes/classify_email.py

"""郵件分類節點 — LLM 智慧分類每封郵件"""

from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import init_chat_model
from src.email_workflow.state import WorkflowState

class EmailClassification(BaseModel):
    """郵件分類結果的結構化輸出格式"""
    category: Literal[
        "complaint", "quote_request", "general", "spam"
    ] = Field(description="郵件分類類別")
    priority: Literal["high", "medium", "low"] = Field(
        description="優先級判定"
    )
    reasoning: str = Field(
        description="分類理由（簡短說明）"
    )
    needs_approval: bool = Field(
        description="是否涉及需要主管審批的內容（如退款、折扣承諾等）"
    )


async def classify_email(state: WorkflowState) -> dict:
    """
    工作流第二站：用 LLM 對每封郵件進行智慧分類
    這就像是收發室小妹拆開每封信，
    快速掃一眼內容，然後在信封上蓋上分類章：
    - 🔴 客訴（complaint）：客戶不爽了，要趕快處理
    - 🟡 報價請求（quote_request）：有人想買東西，商機！
    - 🟢 一般通知（general）：知道就好
    - ⚫ 垃圾信（spam）：直接丟回收桶
    """

    model = init_chat_model("anthropic:claude-sonnet-4-6")
    classified_emails = []

    for email in state.emails:
        # 使用 Structured Output 確保分類結果格式正確
        structured_model = model.with_structured_output(
            EmailClassification
        )

        classification = await structured_model.ainvoke(
            f"""請分析以下郵件並進行分類：
寄件人：{email.sender}
主旨：{email.subject}
內文：{email.body}

分類規則：
1. complaint（客訴）：客戶表達不滿、要求退款、投訴品質問題
2. quote_request（報價請求）：詢問價格、要求報價、批量購買諮詢
3. general（一般）：通知、確認信、內部溝通、一般詢問
4. spam（垃圾信）：廣告、釣魚信、不相關的推銷

優先級規則：
- high：涉及金額超過 10 萬、法律威脅、媒體曝光、VIP 客戶
- medium：一般客訴、正常報價請求
- low：一般通知、垃圾信

需要審批的情況：
- 涉及退款承諾
- 涉及特殊折扣
- 涉及法律或合規問題"""
        )

        # 更新郵件的分類資訊
        email.category = classification.category
        email.priority = classification.priority
        email.needs_approval = classification.needs_approval
        classified_emails.append(email)

    # 更新統計資訊
    stats = {**state.stats}

    for email in classified_emails:
        if email.category == "complaint":
            stats["complaints"] += 1
        elif email.category == "quote_request":
            stats["quotes"] += 1
        elif email.category == "general":
            stats["general"] += 1
        elif email.category == "spam":
            stats["spam"] += 1
    return {
        "emails": classified_emails,
        "workflow_status": "processing",
        "stats": stats,
    }
