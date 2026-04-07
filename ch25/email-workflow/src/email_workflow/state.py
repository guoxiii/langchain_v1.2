# src/email_workflow/state.py

"""工作流狀態定義 — 所有節點共享的資料結構"""

from __future__ import annotations
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

class EmailItem(BaseModel):
    """單封郵件的資料結構"""
    email_id: str = Field(description="郵件唯一識別碼")
    sender: str = Field(description="寄件人")
    subject: str = Field(description="郵件主旨")
    body: str = Field(description="郵件內文（截取前 500 字）")
    received_at: str = Field(description="收件時間")

    category: Literal[
        "complaint", "quote_request", "general", "spam", "unclassified"
    ] = Field(default="unclassified", description="郵件分類")
    priority: Literal["high", "medium", "low"] = Field(
        default="medium", description="優先級"
    )

    action_taken: str = Field(default="", description="已採取的處理動作")

    needs_approval: bool = Field(
        default=False, description="是否需要主管審批"
    )

    approval_status: Literal[
        "pending", "approved", "rejected", "not_required"
    ] = Field(default="not_required", description="審批狀態")

class WorkflowState(BaseModel):
    """
    工作流主狀態 — 整個流程的「簽核單」
    就像是辦公室裡的那張表格，每經過一個部門就多填幾個欄位。
    最後這張表格會變成一份完整的處理報告。
    """
    # 郵件列表 — 本次批次要處理的所有郵件
    emails: list[EmailItem] = Field(default_factory=list)

    # 當前正在處理的郵件索引
    current_index: int = Field(default=0)

    # 處理中的對話訊息（供 Agent 使用）
    messages: Annotated[list, add_messages] = Field(default_factory=list)

    # 報表數據
    report_data: dict = Field(default_factory=dict)

    # 工作流元資料
    workflow_status: Literal[
        "fetching", "classifying", "processing",
        "reporting", "reviewing", "notifying", "completed", "error"
    ] = Field(default="fetching")

    error_log: list[str] = Field(default_factory=list)

    # 統計資訊
    stats: dict = Field(default_factory=lambda: {
        "total": 0,
        "complaints": 0,
        "quotes": 0,
        "general": 0,
        "spam": 0,
        "approved": 0,
        "rejected": 0,
    })
