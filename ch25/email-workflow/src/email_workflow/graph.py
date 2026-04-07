# src/email_workflow/graph.py

"""主工作流圖 — 把所有節點串成一條龍"""

from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.email_workflow.state import WorkflowState
from src.email_workflow.nodes.fetch_emails import fetch_emails
from src.email_workflow.nodes.classify_email import classify_email
from src.email_workflow.nodes.router import (
    route_by_category,
    should_continue_processing,
)
from src.email_workflow.nodes.handle_complaint import handle_complaint
from src.email_workflow.nodes.handle_quote import handle_quote
from src.email_workflow.nodes.handle_general import handle_general
from src.email_workflow.nodes.generate_report import generate_report
from src.email_workflow.nodes.supervisor import supervisor_review
from src.email_workflow.nodes.notify import send_notification

def build_workflow() -> StateGraph:
    """
    建構郵件處理工作流圖
    這就是整個系統的「藍圖」。
    每一個 add_node 就是一個工作站，
    每一個 add_edge 就是工作站之間的輸送帶，
    而 add_conditional_edges 就是輸送帶上的分流閘門。
    """

    # 初始化 StateGraph
    workflow = StateGraph(WorkflowState)

    # === 添加所有節點 ===
    workflow.add_node("fetch_emails", fetch_emails)
    workflow.add_node("classify_emails", classify_email)
    workflow.add_node("route_email", lambda state: state)  # 路由是純邏輯節點
    workflow.add_node("handle_complaint", handle_complaint)
    workflow.add_node("handle_quote", handle_quote)
    workflow.add_node("handle_general", handle_general)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("supervisor_review", supervisor_review)
    workflow.add_node("send_notification", send_notification)

    # === 定義邊（Edge）— 工作站之間的輸送帶 ===
    # 起點 → 抓取郵件
    workflow.add_edge(START, "fetch_emails")

    # 抓取郵件 → 分類郵件
    workflow.add_edge("fetch_emails", "classify_emails")

    # 分類郵件 → 路由（開始逐封處理）
    workflow.add_edge("classify_emails", "route_email")

    # 路由 → 根據分類走不同的處理流程（核心分流邏輯！）
    workflow.add_conditional_edges(
        "route_email",
        route_by_category,
        {
            "handle_complaint": "handle_complaint",
            "handle_quote": "handle_quote",
            "handle_general": "handle_general",
            "generate_report": "generate_report",
        },
    )

    # 各處理節點完成後 → 決定繼續處理還是產生報表
    for handler_node in [
        "handle_complaint", "handle_quote", "handle_general"
    ]:
        workflow.add_conditional_edges(
            handler_node,
            should_continue_processing,
            {
                "route_email": "route_email",
                "generate_report": "generate_report",
            },
        )

    # 報表 → 審批
    workflow.add_edge("generate_report", "supervisor_review")

    # 審批 → 通知
    workflow.add_edge("supervisor_review", "send_notification")

    # 通知 → 結束
    workflow.add_edge("send_notification", END)
    return workflow

def compile_workflow(use_memory: bool = True):
    """
    編譯工作流並加入 Checkpointer
    Checkpointer 就是工作流的「存檔功能」。
    每處理完一個節點就自動存檔，
    萬一中途斷電，下次啟動時可以從最近的存檔點繼續。
    """
    workflow = build_workflow()

    if use_memory:
        checkpointer = MemorySaver()
        graph = workflow.compile(checkpointer=checkpointer)
    else:
        graph = workflow.compile()
    return graph

# === 匯出給 LangGraph Platform 使用 ===
# graph = compile_workflow()
graph = compile_workflow(use_memory=False)
