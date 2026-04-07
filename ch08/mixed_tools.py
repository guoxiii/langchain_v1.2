# ch08/mixed_tools.py
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

# === 方式一：@tool — 簡單的計算工具 ===
@tool
def calculate_discount(price: float, discount_percent: float) -> str:
    """計算折扣後的價格。

    Args:
        price: 原始價格（新台幣）
        discount_percent: 折扣百分比（例如 20 代表打八折）
    """
    final_price = price * (1 - discount_percent / 100)
    saved = price - final_price

    return f"原價 NT${price:,.0f}，打 {100-discount_percent:.0f} 折後為 NT${final_price:,.0f}，省下 NT${saved:,.0f}"

# === 方式二：BaseTool — 需要配置的庫存查詢工具 ===
class InventoryInput(BaseModel):
    product_id: str = Field(description="商品編號，例如 'SKU-001'")

class InventoryTool(BaseTool):
    """查詢商品的即時庫存數量。"""
    name: str = "check_inventory"
    description: str = "查詢指定商品的目前庫存數量。需提供商品編號。"
    args_schema: Type[BaseModel] = InventoryInput

    # 模擬的庫存資料（實際中可能是資料庫連線）
    inventory_db: dict = {
        "SKU-001": {"name": "保濕噴霧", "stock": 150},
        "SKU-002": {"name": "防曬乳", "stock": 0},
        "SKU-003": {"name": "潔面慕斯", "stock": 42},
    }

    def _run(self, product_id: str) -> str:
        item = self.inventory_db.get(product_id)

        if not item:
            return f"找不到商品編號 {product_id}"

        status = "有貨" if item["stock"] > 0 else "缺貨"
        return f"{item['name']}（{product_id}）：庫存 {item['stock']} 件（{status}）"

# === 組合所有工具 ===
model = init_chat_model("google_genai:gemini-2.5-flash")

agent = create_agent(
    model,
    tools=[
        calculate_discount,        # @tool 裝飾器
        InventoryTool(),           # BaseTool 實例
        # MCP 工具則透過 langchain-mcp-adapters 載入後也能放在這裡

    ],

    system_prompt=(
        "你是 PURIFY 保養品牌的智能客服助手。"
        "你可以幫客戶查詢庫存和計算折扣。請用繁體中文回答。"
    )
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "SKU-001 還有貨嗎？如果原價 590 元打 85 折是多少？"}]}
)

for msg in result["messages"]:
    if hasattr(msg, "content") and msg.content:
        print(f"[{msg.type}] {msg.content}")
