# 檔案名稱：ch04/agent_stream.py

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

@tool
def get_weather(location: str) -> str:
    """查詢指定城市的天氣資訊。

    Args:
        location: 城市名稱
    """

    return f"{location}：28°C，晴天"

@tool
def calculate(expression: str) -> str:
    """計算數學表達式。

    Args:

        expression: 數學表達式字串
    """

    try:
        return str(eval(expression))
    except Exception as e:
        return f"錯誤：{e}"

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_weather, calculate],
    system_prompt="你是一個實用的生活助手，用繁體中文回答。",
)

# 使用 stream 觀察 Agent 的每一步
print("Agent 開始工作...\n")

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "查一下台北天氣，然後幫我算 1500 除以 3 等於多少"}]},
    stream_mode="updates",
):

    # chunk 是一個字典，key 是節點名稱（"model" 或 "tools"）
    for node_name, updates in chunk.items():
        print(f"--- {node_name} 節點 ---")

        if "messages" in updates:
            for msg in updates["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:

                    for tc in msg.tool_calls:
                        print(f"  🔧 呼叫工具：{tc['name']}({tc['args']})")
                elif msg.content:
                    print(f"  💬 {msg.content[:100]}...")

        print()