# src/email_workflow/nodes/router.py

"""路由邏輯 — conditional edges 的核心"""

from __future__ import annotations
from typing import Literal
from src.email_workflow.state import WorkflowState

def route_by_category(
    state: WorkflowState,
) -> Literal[
    "handle_complaint", "handle_quote", "handle_general", "generate_report"
]:
    """
    根據當前郵件的分類決定下一個處理節點
    這個函式就是交流道上的路標：
    - 客訴 → 客訴處理部門
    - 報價 → 報價處理部門
    - 一般/垃圾 → 一般處理部門
    - 所有郵件都處理完了 → 產生報表

    Returns:
        下一個要執行的節點名稱
    """

    # 檢查是否還有未處理的郵件
    if state.current_index >= len(state.emails):
        return "generate_report"

    current_email = state.emails[state.current_index]

    match current_email.category:
        case "complaint":
            return "handle_complaint"
        case "quote_request":
            return "handle_quote"
        case _:
            # general 和 spam 都走一般處理
            return "handle_general"

def should_continue_processing(
    state: WorkflowState,
) -> Literal["route_email", "generate_report"]:
    """
    處理完一封郵件後，決定是繼續處理下一封還是產生報表
    這像是工廠產線上的計數器：
    一個零件加工完，看看還有沒有下一個。
    """

    if state.current_index < len(state.emails):
        return "route_email"
    else:
        return "generate_report"
