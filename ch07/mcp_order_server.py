# mcp_order_server.py

"""供 interceptor_context.py 測試用的簡易 MCP Server"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my_service")

# 模擬訂單資料庫
FAKE_ORDERS = {
    "user_123": [
        {"order_id": "A001", "item": "無線藍牙耳機", "status": "已出貨"},
        {"order_id": "A002", "item": "機械鍵盤", "status": "處理中"},
    ],
    "user_456": [
        {"order_id": "B001", "item": "螢幕保護貼", "status": "已送達"},
    ],
}

@mcp.tool()
def query_orders(user_id: str = "", language: str = "zh-TW") -> str:
    """查詢使用者的訂單資訊。

    Args:
        user_id: 使用者 ID
        language: 回應語言
    """
    orders = FAKE_ORDERS.get(user_id, [])

    if not orders:
        return f"找不到 {user_id} 的訂單資料。"

    lines = [f"【{user_id} 的訂單】(語言：{language})"]

    for o in orders:
        lines.append(
            f"  - 訂單 {o['order_id']}：{o['item']}（{o['status']}）"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")