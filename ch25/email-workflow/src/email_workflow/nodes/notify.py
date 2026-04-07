# src/email_workflow/nodes/notify.py

"""通知發送節點 — 讓所有人知道今天的處理結果"""

from __future__ import annotations
from src.email_workflow.state import WorkflowState

async def send_notification(state: WorkflowState) -> dict:
    """
    發送通知 — 工作流的最後一站

    在生產環境中，這裡可以：
    - 透過 MCP 連接 Slack 發送摘要
    - 透過 Gmail MCP 發送郵件報告
    - 透過 Webhook 通知外部系統

    本範例簡化為終端機輸出。
    """
    report = state.report_data
    notification = f"""
📧 每日郵件處理報告完成

📊 處理統計：
• 總計處理：{state.stats['total']:>3} 封
• 客訴：    {state.stats['complaints']:>3} 封
• 報價：    {state.stats['quotes']:>3} 封
• 一般：    {state.stats['general']:>3} 封
• 垃圾信：  {state.stats['spam']:>3} 封

✅ 審批結果：
• 已批准：  {state.stats['approved']:>3} 件
 • 已退回：  {state.stats['rejected']:>3} 件
    """

    print(notification)

    return {
        "workflow_status": "completed",
    }
