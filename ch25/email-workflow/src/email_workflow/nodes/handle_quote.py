# src/email_workflow/nodes/handle_quote.py

"""報價處理節點 — 把握每一個商機"""

from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from src.email_workflow.state import WorkflowState

async def handle_quote(state: WorkflowState) -> dict:
    """
    處理報價請求郵件

    報價處理的重點是：
    1. 提取客戶需求的商品/服務
    2. 根據標準價目表產生報價單草稿
    3. 標記需要業務主管確認的特殊折扣

    這就像是業務部門的報價流程自動化。
    """

    current_email = state.emails[state.current_index]
    model = init_chat_model("anthropic:claude-sonnet-4-6")

    response = await model.ainvoke(
        f"""你是一位專業的業務助理。請針對以下報價請求：

寄件人：{current_email.sender}
主旨：{current_email.subject}
內文：{current_email.body}

請產生：
1. 客戶需求摘要
2. 建議報價方向（根據常見產品/服務定價邏輯）
3. 回覆草稿（專業、清楚列出項目與預估價格範圍）
4. 是否需要特殊折扣或主管核准

請以繁體中文回覆。"""
    )

    emails = list(state.emails)
    emails[state.current_index].action_taken = response.content

    if emails[state.current_index].needs_approval:
        emails[state.current_index].approval_status = "pending"

    return {
        "emails": emails,
        "current_index": state.current_index + 1,
    }
