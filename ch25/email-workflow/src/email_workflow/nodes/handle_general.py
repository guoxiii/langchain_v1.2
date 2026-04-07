# src/email_workflow/nodes/handle_general.py

"""一般郵件處理節點 — 簡單但不馬虎"""

from __future__ import annotations
from src.email_workflow.state import WorkflowState


async def handle_general(state: WorkflowState) -> dict:
    """
    處理一般郵件和垃圾信

    一般郵件：簡單記錄即可
    垃圾信：標記為已讀，不做其他處理

    這就像是收發室小妹對一般信件的處理方式：
    看一眼，知道了，歸檔。
    """

    current_email = state.emails[state.current_index]
    emails = list(state.emails)

    if current_email.category == "spam":
        emails[state.current_index].action_taken = "已標記為垃圾信，不做處理"
    else:
        emails[state.current_index].action_taken = "已閱讀並歸檔"

    return {
        "emails": emails,
        "current_index": state.current_index + 1,
    }
