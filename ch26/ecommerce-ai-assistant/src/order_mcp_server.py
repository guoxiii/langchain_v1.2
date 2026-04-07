# src/order_mcp_server.py

"""
訂單查詢 MCP Server
使用 FastMCP 建立標準化的訂單查詢服務
"""

import json
import random
from fastmcp import FastMCP

# 建立 MCP Server
mcp = FastMCP("order-query-server")

# ============================================================
# 模擬訂單資料庫
# ============================================================

MOCK_ORDERS = {
    "ORD-202501-001": {
        "order_id": "ORD-202501-001",
        "customer_id": "C1001",
        "customer_name": "王小明",
        "items": [
            {"product_id": "P001", "product_name": "控油潔面凝膠", "quantity": 2, "unit_price": 380},
            {"product_id": "P002", "product_name": "保濕控油化妝水", "quantity": 1, "unit_price": 420},
        ],
        "total_amount": 1180,
        "status": "已出貨",
        "shipping_status": "配送中",
        "tracking_number": "TW123456789",
        "order_date": "2025-01-15",
        "estimated_delivery": "2025-01-18",
        "shipping_address": "台北市大安區...",
        "payment_method": "信用卡",
    },
    "ORD-202501-002": {
        "order_id": "ORD-202501-002",
        "customer_id": "C1002",
        "customer_name": "李小華",
        "items": [
            {"product_id": "P005", "product_name": "毛孔緊緻精華液", "quantity": 1, "unit_price": 680},
            {"product_id": "P006", "product_name": "舒緩修復面膜", "quantity": 5, "unit_price": 180},
        ],
        "total_amount": 1580,
        "status": "處理中",
        "shipping_status": "備貨中",
        "tracking_number": None,
        "order_date": "2025-01-20",
        "estimated_delivery": "2025-01-25",
        "shipping_address": "台中市西區...",
        "payment_method": "LINE Pay",
    },
    "ORD-202501-003": {
        "order_id": "ORD-202501-003",
        "customer_id": "C1001",
        "customer_name": "王小明",
        "items": [
            {"product_id": "P003", "product_name": "清爽防曬乳 SPF50+", "quantity": 3, "unit_price": 520},
        ],
        "total_amount": 1560,
        "status": "已完成",
        "shipping_status": "已送達",
        "tracking_number": "TW987654321",
        "order_date": "2025-01-10",
        "estimated_delivery": "2025-01-13",
        "actual_delivery": "2025-01-12",
        "shipping_address": "台北市大安區...",
        "payment_method": "蝦皮錢包",
    },
}

# ============================================================
# MCP 工具定義
# ============================================================

@mcp.tool()
def query_order_by_id(order_id: str) -> str:
    """
    根據訂單編號查詢訂單詳細資訊。    

    Args:
        order_id: 訂單編號，格式如 "ORD-202501-001"    

    Returns:
        訂單詳細資訊的 JSON 字串
    """

    order = MOCK_ORDERS.get(order_id)

    if order:
        return json.dumps(order, ensure_ascii=False, indent=2)

    return json.dumps(
        {"error": f"找不到訂單 {order_id}，請確認訂單編號是否正確"},
        ensure_ascii=False,
    )

@mcp.tool()
def query_orders_by_customer(customer_id: str) -> str:
    """
    根據顧客編號查詢該顧客的所有訂單。    

    Args:
        customer_id: 顧客編號，格式如 "C1001"    

    Returns:

        該顧客所有訂單的摘要列表
    """

    customer_orders = [
        {
            "order_id": order["order_id"],
            "order_date": order["order_date"],
            "total_amount": order["total_amount"],
            "status": order["status"],
            "item_count": len(order["items"]),
        }

        for order in MOCK_ORDERS.values()
        if order["customer_id"] == customer_id
    ]

    if customer_orders:
        return json.dumps({
            "customer_id": customer_id,
            "total_orders": len(customer_orders),
            "orders": customer_orders,
        }, ensure_ascii=False, indent=2)

    return json.dumps(
        {"error": f"找不到顧客 {customer_id} 的訂單紀錄"},
        ensure_ascii=False,
    )

@mcp.tool()
def track_shipment(tracking_number: str) -> str:
    """
    追蹤物流配送狀態。    

    Args:
        tracking_number: 物流追蹤編號    

    Returns:
        物流追蹤資訊
    """

    # 模擬物流追蹤
    tracking_info = {
        "TW123456789": {
            "tracking_number": "TW123456789",
            "carrier": "黑貓宅急便",
            "status": "配送中",
            "history": [
                {"time": "2025-01-16 09:00", "event": "已從倉庫出貨"},
                {"time": "2025-01-16 14:00", "event": "到達台北轉運中心"},
                {"time": "2025-01-17 08:00", "event": "配送司機已取件"},
                {"time": "2025-01-17 10:30", "event": "配送中，預計今日 12:00-18:00 送達"},
            ],
        },
        "TW987654321": {
            "tracking_number": "TW987654321",
            "carrier": "黑貓宅急便",
            "status": "已送達",
            "history": [
                {"time": "2025-01-11 09:00", "event": "已從倉庫出貨"},
                {"time": "2025-01-11 15:00", "event": "到達台北轉運中心"},
                {"time": "2025-01-12 10:00", "event": "配送司機已取件"},
                {"time": "2025-01-12 14:30", "event": "已送達，由管理室代收"},
            ],
        },
    }

    info = tracking_info.get(tracking_number)

    if info:
        return json.dumps(info, ensure_ascii=False, indent=2)

    return json.dumps(
        {"error": f"找不到追蹤編號 {tracking_number} 的物流資訊"},
        ensure_ascii=False,
    )

@mcp.tool()
def request_return(order_id: str, reason: str) -> str:
    """
    提交退貨/退款申請。    

    Args:
        order_id: 訂單編號
        reason: 退貨原因    

    Returns:
        退貨申請結果
    """
    order = MOCK_ORDERS.get(order_id)

    if not order:
        return json.dumps(
            {"error": f"找不到訂單 {order_id}"},
            ensure_ascii=False,
        )

    if order["status"] not in ["已完成", "已出貨"]:
        return json.dumps(
            {"error": f"訂單目前狀態為「{order['status']}」，無法申請退貨"},
            ensure_ascii=False,
        )

    return_id = f"RET-{random.randint(100000, 999999)}"

    return json.dumps({
        "return_id": return_id,
        "order_id": order_id,
        "status": "申請已提交",
        "reason": reason,
        "message": f"退貨申請 {return_id} 已成功提交，客服人員將在 1-2 個工作天內與您聯繫確認。",
        "refund_estimate": f"退款金額 NT${order['total_amount']}，預計 5-7 個工作天退回原付款方式。",
    }, ensure_ascii=False, indent=2)

# ============================================================
# 啟動 MCP Server
# ============================================================

if __name__ == "__main__":
    # 使用 stdio 傳輸方式啟動
    mcp.run(transport="stdio")
