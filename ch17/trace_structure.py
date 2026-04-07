# ch17/trace_structure.py

"""觀察 Agent 的 Trace 結構"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

@tool
def get_weather(city: str) -> str:
    """查詢指定城市的天氣資訊。"""
    # 模擬天氣資料
    weather_data = {
        "台北": "晴天，28°C，濕度 65%",
        "東京": "多雲，22°C，濕度 70%",
        "紐約": "下雨，15°C，濕度 85%",
    }

    return weather_data.get(city, f"找不到 {city} 的天氣資訊")

@tool
def get_population(city: str) -> str:
    """查詢指定城市的人口數。"""
    population_data = {
        "台北": "約 250 萬人",
        "東京": "約 1,400 萬人",
        "紐約": "約 830 萬人",
    }

    return population_data.get(city, f"找不到 {city} 的人口資訊")

# 初始化模型
llm = init_chat_model("google_genai:gemini-2.5-flash")

# 建立 Agent
agent = create_agent(
    model=llm,
    tools=[get_weather, get_population],
    system_prompt="你是一個旅遊資訊助手，能查詢城市的天氣和人口資訊。",
)

# 執行 Agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "台北現在天氣如何？人口有多少？"}]}
)

# 印出最終回覆
for msg in result["messages"]:
    print(f"[{msg.type}] {msg.text[:200]}")
