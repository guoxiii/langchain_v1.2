# src/email_workflow/nodes/handle_complaint.py

"""客訴處理節點 — 認真對待每一位不開心的客戶"""

from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from src.email_workflow.state import WorkflowState

async def handle_complaint(state: WorkflowState) -> dict:
    """
    處理客訴郵件

    客訴處理的重點是：
    1. 理解客戶的核心訴求
    2. 產生一封得體的回覆草稿
    3. 標記是否需要主管審批（退款/折扣）

    就像是客服部門收到投訴信後的標準作業流程，
    只不過現在 AI 幫你先把苦差事做完了。
    """
    current_email = state.emails[state.current_index]
    model = init_chat_model("anthropic:claude-sonnet-4-6")

    response = await model.ainvoke(
        f"""你是一位專業的客服處理人員。請針對以下客訴郵件：

寄件人：{current_email.sender}
主旨：{current_email.subject}
內文：{current_email.body}

請產生：
1. 客訴摘要（一句話）
2. 建議回覆草稿（專業、誠懇、有解決方案）
3. 建議的處理動作（如：道歉回覆 / 安排退款 / 轉交主管）

請以繁體中文回覆。"""
    )

    # 更新郵件狀態
    emails = list(state.emails)
    emails[state.current_index].action_taken = response.content

    if emails[state.current_index].needs_approval:
        emails[state.current_index].approval_status = "pending"

    return {
        "emails": emails,
        "current_index": state.current_index + 1,
    }
