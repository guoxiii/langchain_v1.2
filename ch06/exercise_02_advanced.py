# ch06/exercise_02_advanced.py

"""練習二：搭配工具的結構化報表 Agent"""
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool

load_dotenv()

# ---------- 定義工具 ----------
@tool
def get_product_info(product_name: str) -> str:
    """查詢產品的基本資訊，包含價格、上市日期、品牌等"""
    # 模擬產品資料庫
    products = {
        "MacBook Pro": "品牌：Apple，價格：NT$59,900 起，上市：2025年10月，類別：筆記型電腦",
        "AirPods Pro": "品牌：Apple，價格：NT$7,990，上市：2025年9月，類別：無線耳機",
        "iPhone 17": "品牌：Apple，價格：NT$32,900 起，上市：2025年9月，類別：智慧型手機",
        "Galaxy S26": "品牌：Samsung，價格：NT$29,900 起，上市：2026年1月，類別：智慧型手機",
    }

    for key, value in products.items():
        if key.lower() in product_name.lower():
            return value

    return f"找不到產品「{product_name}」的資訊"
@tool
def get_market_average_score(category: str) -> str:
    """查詢該產品類別的市場平均評分"""
    averages = {
        "筆記型電腦": "市場平均評分：4.2/5，平均價格：NT$35,000",
        "無線耳機": "市場平均評分：3.8/5，平均價格：NT$4,500",
        "智慧型手機": "市場平均評分：4.0/5，平均價格：NT$25,000",
    }

    return averages.get(category, f"找不到「{category}」類別的市場資訊")

# ---------- 定義結構化輸出 ----------
class ProductReport(BaseModel):
    """產品分析報表"""
    product_name: str = Field(description="產品名稱")
    brand: str = Field(description="品牌")
    price_range: str = Field(description="價格範圍")
    category: str = Field(description="產品類別")

    user_rating: float = Field(
        description="根據評論推斷的使用者評分（1.0-5.0）",
        ge=1.0,
        le=5.0,
    )

    market_comparison: str = Field(
        description="與市場平均的比較分析"
    )

    strengths: list[str] = Field(description="產品優勢（根據評論）")
    weaknesses: list[str] = Field(description="產品劣勢（根據評論）")
    verdict: str = Field(description="最終評價，100 字以內")

# ---------- 錯誤處理 ----------
def report_error_handler(error: Exception) -> str:
    error_msg = str(error)

    if "user_rating" in error_msg:
        return "使用者評分必須介於 1.0 到 5.0 之間。請修正後重新回答。"

    return f"報表格式有誤，請修正：{error_msg}"

# ---------- 建立 Agent ----------
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_product_info, get_market_average_score],
    response_format=ToolStrategy(
        schema=ProductReport,
        handle_errors=report_error_handler,
    ),

    system_prompt=(
        "你是一個產品分析師。收到使用者的產品評論後，請：\n"
        "1. 先用工具查詢產品基本資訊\n"
        "2. 再用工具查詢該類別的市場平均分數\n"
        "3. 最後綜合所有資訊，產出結構化的分析報表\n"
        "所有分析必須基於評論內容和查詢到的資料，不要憑空捏造。"
    ),
)

# ---------- 執行 ----------
review_text = """
我買了 MacBook Pro 已經用了兩個月，整體來說非常滿意。
M4 晶片的效能真的沒話說，跑 Python 的 AI 模型訓練速度飛快。
螢幕素質一流，色彩準確度很高，修圖剪片都很舒服。
鍵盤手感也比前幾代好很多，打字打一整天都不累。
電池續航也很猛，正常使用可以撐一整天。
缺點的話，價格確實偏高，接口還是只有 Thunderbolt，
偶爾會需要轉接頭有點麻煩。重量對於常出差的人來說也稍嫌重了點。
但整體來說，這是我用過最好的筆電，強烈推薦給開發者和創作者！
"""

result = agent.invoke({
    "messages": [{"role": "user", "content": f"請分析以下評論：\n{review_text}"}]
})

# 印出完整報表
report = result["structured_response"]

print("=" * 60)
print(f"📊 產品分析報表")
print("=" * 60)
print(f"產品：{report.product_name}（{report.brand}）")
print(f"類別：{report.category}")
print(f"價格：{report.price_range}")
print(f"使用者評分：{'⭐' * int(report.user_rating)} {report.user_rating}/5.0")

print(f"\n📈 市場比較：{report.market_comparison}")
print(f"\n✅ 優勢：")

for s in report.strengths:
    print(f"   • {s}")

print(f"\n⚠️ 劣勢：")

for w in report.weaknesses:
    print(f"   • {w}")

print(f"\n📝 最終評價：{report.verdict}")
print("=" * 60)
