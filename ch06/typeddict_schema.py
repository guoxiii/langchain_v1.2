# ch06/typeddict_schema.py

"""使用 TypedDict 定義 Schema"""
from dotenv import load_dotenv
from typing import TypedDict
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

class WeatherInfo(TypedDict):
    """天氣資訊"""
    city: str          # 城市名稱
    temperature: float # 氣溫（攝氏）
    condition: str     # 天氣狀況
    humidity: int      # 濕度百分比

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(WeatherInfo),
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "台北今天天氣大概 28 度，多雲，濕度 75%"
    }]
})

# TypedDict 回傳的是 dict，不是 Pydantic Model
weather = result["structured_response"]

print(type(weather))  # <class 'dict'>
print(weather)  # {'city': '台北', 'temperature': 28.0, 'condition': '多雲', 'humidity': 75}
