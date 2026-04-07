# src/mcp_servers/ticket_server.py

"""
工單系統 MCP Server。
使用 FastMCP 建立，模擬一個工單管理系統。
在真實環境中，這裡會連接到 Jira、Zendesk 等工單系統的 API。
"""

import json
import uuid
from datetime import datetime
from fastmcp import FastMCP

# 建立 MCP Server
mcp = FastMCP(
    name="ticket-system",
    instructions="工單管理系統，用於建立、查詢和更新客服工單。",
)

# 模擬工單資料庫（真實環境中會連接到實際資料庫）
TICKETS_DB: dict[str, dict] = {}

@mcp.tool()
def create_ticket(
    customer_name: str,
    order_id: str,
    issue_type: str,
    description: str,
    priority: str = "medium",
) -> str:
    """建立新的客服工單。
    當客戶遇到需要追蹤處理的問題時（如商品瑕疵、物流異常），
    使用此工具建立工單。

    Args:
        customer_name: 客戶姓名
        order_id: 相關訂單編號
        issue_type: 問題類型（product_defect / wrong_item / shipping_issue / refund_request / other）
        description: 問題的詳細描述
        priority: 優先級（low / medium / high / urgent）

    Returns:

        JSON 格式的工單建立結果，包含工單編號
    """

    ticket_id = f"TK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    ticket = {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "order_id": order_id,
        "issue_type": issue_type,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "assigned_to": None,
    }

    TICKETS_DB[ticket_id] = ticket

    return json.dumps(
        {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"工單 {ticket_id} 已成功建立，客服團隊將盡快處理。",
            "estimated_response_time": "24 小時內",
        },
        ensure_ascii=False,
    )

@mcp.tool()
def get_ticket_status(ticket_id: str) -> str:
    """查詢工單狀態。

    Args:
        ticket_id: 工單編號（格式：TK-YYYYMMDD-XXXXXX）

    Returns:
        JSON 格式的工單狀態資訊
    """

    ticket = TICKETS_DB.get(ticket_id)

    if not ticket:
        return json.dumps(
            {"success": False, "message": f"找不到工單 {ticket_id}"},
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "success": True,
            "ticket": ticket,
        },
        ensure_ascii=False,
    )

@mcp.tool()
def update_ticket(
    ticket_id: str,
    status: str | None = None,
    note: str | None = None,
) -> str:
    """更新工單狀態或新增備註。

    Args:
        ticket_id: 工單編號
        status: 新狀態（open / in_progress / resolved / closed）
        note: 要新增的備註內容

    Returns:
        JSON 格式的更新結果
    """

    ticket = TICKETS_DB.get(ticket_id)

    if not ticket:
        return json.dumps(
            {"success": False, "message": f"找不到工單 {ticket_id}"},
            ensure_ascii=False,
        )

    if status:
        ticket["status"] = status

    if note:
        ticket.setdefault("notes", []).append(
            {"content": note, "timestamp": datetime.now().isoformat()}
        )

    return json.dumps(
        {"success": True, "message": f"工單 {ticket_id} 已更新"},
        ensure_ascii=False,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
