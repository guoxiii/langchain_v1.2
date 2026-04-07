# ch08/param_description.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Literal

class OrderQueryInput(BaseModel):
    """訂單查詢參數。"""
    order_id: str = Field(
        description="訂單編號，格式為 ORD-YYYYMMDD-XXXX，例如 'ORD-20250315-0042'"
    )
    include_items: bool = Field(
        default=False,
        description="是否包含訂單中的商品明細。設為 True 會回傳更詳細的資訊。"
    )
    status_filter: Literal["all", "pending", "shipped", "delivered", "cancelled"] = Field(
        default="all",
        description="篩選訂單狀態：all=全部、pending=待處理、shipped=已出貨、delivered=已送達、cancelled=已取消"
    )

@tool(args_schema=OrderQueryInput)
def query_order(order_id: str, include_items: bool = False, status_filter: str = "all") -> str:
    """查詢訂單的詳細資訊，包括狀態、金額和物流追蹤。
    使用此工具來回答使用者關於訂單狀態、出貨進度、退貨退款等問題。
    如果使用者沒有提供完整的訂單編號，請先詢問。
    """
    return f"訂單 {order_id} 的查詢結果（items={include_items}, filter={status_filter}）"
