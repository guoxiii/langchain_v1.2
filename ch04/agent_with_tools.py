# 檔案名稱：ch04/agent_with_tools.py

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

# ----- 定義工具 -----
@tool
def get_weather(location: str) -> str:
    """查詢指定城市的天氣資訊。

    Args:
        location: 城市名稱，例如「台北」、「東京」
    """

    weather_data = {
        "台北": "28°C，晴天，濕度 65%",
        "東京": "22°C，多雲，濕度 70%",
        "紐約": "15°C，陰天，濕度 55%",
    }

    return weather_data.get(location, f"抱歉，找不到 {location} 的天氣資訊")

@tool
def calculate(expression: str) -> str:
    """計算數學表達式並回傳結果。

    Args:
        expression: 數學表達式字串，例如 "2 + 3 * 4" 或 "100 / 3"
    """
    try:
        # 使用 Python 內建的 eval 進行計算
        # 注意：生產環境應使用更安全的數學運算庫
        result = eval(expression)
        return f"計算結果：{result}"
    except Exception as e:
        return f"計算錯誤：{e}"

# ----- 建立 Agent -----
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_weather, calculate],
)

# ----- 執行 Agent -----
result = agent.invoke(
    {"messages": [{"role": "user", "content": "台北今天天氣如何？如果溫度超過 25 度，幫我算 3 人份的冰品預算（每人 85 元）"}]}
)

# 印出完整對話過程
for message in result["messages"]:
    print(f"\n{'='*60}")
    print(f"[{message.type}]")

    if hasattr(message, "tool_calls") and message.tool_calls:
        for tc in message.tool_calls:
            print(f"  → 呼叫工具：{tc['name']}({tc['args']})")

    if message.content:
        print(f"  {message.content}")
