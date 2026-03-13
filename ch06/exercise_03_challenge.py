# ch06/exercise_03_challenge.py

"""練習三：使用 Union Types 的智能分析 Agent"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

# 定義三種不同的報表格式
class TechProductReport(BaseModel):
    """3C 科技產品分析報表"""
    product_name: str = Field(description="產品名稱")
    specs_rating: float = Field(description="規格評分 1-5", ge=1, le=5)
    value_rating: float = Field(description="性價比評分 1-5", ge=1, le=5)
    best_for: list[str] = Field(description="最適合的使用族群")
    verdict: str = Field(description="科技產品評價")

class FoodReport(BaseModel):
    """餐飲美食分析報表"""
    restaurant_name: str = Field(description="餐廳名稱")
    cuisine_type: str = Field(description="料理類型")
    taste_rating: float = Field(description="口味評分 1-5", ge=1, le=5)
    service_rating: float = Field(description="服務評分 1-5", ge=1, le=5)
    price_level: str = Field(description="價位（平價/中等/高檔）")
    must_try_dishes: list[str] = Field(description="推薦必點菜色")

class TravelReport(BaseModel):
    """旅遊景點分析報表"""
    destination: str = Field(description="景點名稱")
    best_season: str = Field(description="最佳旅遊季節")
    budget_estimate: str = Field(description="預估旅費")
    highlights: list[str] = Field(description="亮點")
    tips: list[str] = Field(description="旅遊小提醒")

# 使用 Union Types — Agent 會自動選擇合適的格式
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(
        TechProductReport | FoodReport | TravelReport
    ),

    system_prompt=(
        "你是一個萬能分析師。根據使用者的描述內容，"
        "自動判斷是科技產品、餐飲美食、還是旅遊景點，"
        "並選擇對應的報表格式來回覆。"
    ),
)

# 測試三種不同類型的輸入
test_inputs = [
    "最新的 iPad Air 真的很輕薄，M3 晶片效能夠用，價格也合理。很適合學生和輕度創作者。",
    "上週去了台北的「鼎泰豐」，小籠包依然是一絕，皮薄餡多湯汁鮮美。服務態度非常好，就是排隊時間有點久。人均大約 500-800 元。",
    "去年去了日本京都，秋天的楓紅真的美到不行。建議住在祇園附近，交通方便。記得提前預約嵐山竹林的導覽，還有帶一件薄外套，早晚溫差大。",
]

for input_text in test_inputs:
    result = agent.invoke({
        "messages": [{"role": "user", "content": input_text}]
    })

    response = result["structured_response"]
    report_type = type(response).__name__

    print(f"\n{'='*50}")
    print(f"📋 報表類型：{report_type}")
    print(f"{'='*50}")

    if isinstance(response, TechProductReport):
        print(f"產品：{response.product_name}")
        print(f"規格：{response.specs_rating}/5  性價比：{response.value_rating}/5")
        print(f"適合：{', '.join(response.best_for)}")
        print(f"評價：{response.verdict}")
    elif isinstance(response, FoodReport):
        print(f"餐廳：{response.restaurant_name}（{response.cuisine_type}）")
        print(f"口味：{response.taste_rating}/5  服務：{response.service_rating}/5")
        print(f"價位：{response.price_level}")
        print(f"必點：{', '.join(response.must_try_dishes)}")
    elif isinstance(response, TravelReport):
        print(f"景點：{response.destination}")
        print(f"最佳季節：{response.best_season}")
        print(f"預估旅費：{response.budget_estimate}")
        print(f"亮點：{', '.join(response.highlights)}")
        print(f"小提醒：{', '.join(response.tips)}")
