# src/email_workflow/nodes/supervisor.py

"""審批節點 — Supervisor Agent 負責最終把關"""

from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import init_chat_model
from src.email_workflow.state import WorkflowState

class ApprovalDecision(BaseModel):
    """審批決定的結構化輸出"""
    email_id: str = Field(description="被審批的郵件 ID")
    decision: Literal["approved", "rejected"] = Field(
        description="審批決定"
    )
    reason: str = Field(description="審批理由")
    modified_action: str = Field(
        default="",
        description="如果退回，建議修改的處理方式"
    )

async def supervisor_review(state: WorkflowState) -> dict:
    """
    Supervisor Agent 審批流程
    這個節點扮演的是「主管」的角色。

    它會：
    1. 找出所有標記為「待審批」的郵件
    2. 審閱每封郵件的處理動作
    3. 做出批准或退回的決定

    在生產環境中，這裡可以改為 Human-in-the-Loop，
    真正讓人類主管來審核。
    本範例先用 LLM 模擬主管的判斷邏輯。
    """

    # 使用更高能力的模型作為 Supervisor
    # 「主管」的腦袋當然要比「員工」好一點嘛
    model = init_chat_model("anthropic:claude-sonnet-4-6")
    structured_model = model.with_structured_output(ApprovalDecision)
    emails = list(state.emails)
    stats = {**state.stats}

    for i, email in enumerate(emails):
        if email.approval_status != "pending":
            continue

        # Supervisor 審核每一個待審批的案件
        decision = await structured_model.ainvoke(
            f"""你是一位資深主管，正在審核以下郵件的處理方案：

原始郵件：
- 寄件人：{email.sender}
- 主旨：{email.subject}
- 分類：{email.category}
- 優先級：{email.priority}

處理人員的建議動作：
{email.action_taken}

審核規則：
1. 退款金額在 1 萬元以下 → 可直接批准
2. 退款金額超過 1 萬元 → 需要附上更詳細的調查報告才能批准
3. 特殊折扣超過 20% → 需要業務總監額外確認，先退回
4. 涉及法律問題 → 退回，轉交法務部門
5. 回覆語氣不當 → 退回，要求修改措辭

請以 email_id='{email.email_id}' 做出審批決定。"""
        )

        emails[i].approval_status = decision.decision

        if decision.decision == "approved":
            stats["approved"] += 1
        else:
            stats["rejected"] += 1

            # 如果退回，附上修改建議
            if decision.modified_action:
                emails[i].action_taken += (
                    f"\n\n---\n⚠️ 主管退回意見：{decision.reason}\n"
                    f"建議修改：{decision.modified_action}"
                )

    return {
        "emails": emails,
        "stats": stats,
        "workflow_status": "notifying",
    }
