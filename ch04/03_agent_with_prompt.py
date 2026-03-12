# 檔案名稱：ch04/03_agent_with_prompt.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

@tool
def get_weather(location: str) -> str:
    """查詢指定城市的天氣資訊，包含溫度、天氣狀況和濕度。

    Args:
        location: 城市名稱，例如「台北」、「高雄」
    """

    weather_data = {
        "台北": "28°C，晴天，濕度 65%，紫外線指數 8（高）",
        "高雄": "32°C，晴天，濕度 75%，紫外線指數 10（極高）",
        "花蓮": "26°C，多雲，濕度 60%，紫外線指數 6（中等）",
    }

    return weather_data.get(location, f"抱歉，找不到 {location} 的天氣資訊")

@tool
def calculate(expression: str) -> str:
    """計算數學表達式並回傳結果。

    Args:
        expression: 數學表達式字串，例如 "2 + 3 * 4"
    """

    try:
        result = eval(expression)
        return f"{result}"
    except Exception as e:
        return f"計算錯誤：{e}"

# 用心設計的 system_prompt
system_prompt = """你是一個專業的台灣旅遊助手。

## 行為規範
- 一律使用繁體中文回答
- 語氣活潑親切，像朋友聊天一樣
- 回答天氣問題時，順便給出穿搭建議和旅遊小提醒

## 回覆格式
- 天氣回報後，加上一個 emoji 表情
- 如果溫度超過 30 度，提醒使用者注意防曬和補充水分
- 計算結果要清楚列出計算過程
"""

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_weather, calculate],
    system_prompt=system_prompt,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "我打算這週末去高雄玩，天氣怎麼樣？三個人搭高鐵來回一人 1490 元，幫我算總交通費"}]}
)

# 印出最後的 AI 回覆
for msg in result["messages"]:
    if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
        print(msg.content)
