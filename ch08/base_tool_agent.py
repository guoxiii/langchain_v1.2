# ch08/base_tool_agent.py
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

# 假設 WeatherTool 已定義如上
# weather_tool = WeatherTool(api_key=os.getenv("OPENWEATHER_API_KEY"))
# 如果沒有 API key，用一個簡化版示範
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class CityInput(BaseModel):
    city: str = Field(description="城市名稱")

class SimpleWeatherTool(BaseTool):
    """查詢城市天氣的簡化版工具。"""
    name: str = "get_weather"
    description: str = "查詢指定城市的天氣狀況。請提供城市名稱。"
    args_schema: Type[BaseModel] = CityInput

    def _run(self, city: str) -> str:
        # 模擬資料（實際應用中應呼叫真實 API）
        weather_data = {
            "台北": "晴天，28°C，濕度 75%",
            "東京": "多雲，22°C，濕度 60%",
            "紐約": "雨天，15°C，濕度 85%",
        }

        return weather_data.get(city, f"抱歉，找不到 {city} 的天氣資料")
# 建立 Agent
model = init_chat_model("google_genai:gemini-2.5-flash")
weather = SimpleWeatherTool()
agent = create_agent(
    model,
    tools=[weather],
    system_prompt="你是一個天氣助手，用繁體中文回答。"
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "東京和台北今天天氣如何？"}]}
)

for msg in result["messages"]:
    print(f"[{msg.type}] {msg.content}")
