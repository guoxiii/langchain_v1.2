# 檔案名稱：ch04/06_agent_memory.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

@tool
def calculate(expression: str) -> str:
    """計算數學表達式並回傳結果。

    Args:
        expression: 數學表達式字串
    """

    try:
        return str(eval(expression))
    except Exception as e:
        return f"計算錯誤：{e}"

# 建立記憶機制
memory = MemorySaver()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[calculate],
    system_prompt="你是一個友善的數學助手，用繁體中文回答。記住使用者之前說過的內容。",
    checkpointer=memory,  # 啟用記憶功能
)

# 使用 thread_id 來識別不同的對話
config = {"configurable": {"thread_id": "math-conversation-001"}}

# 第一輪對話
print("=== 第一輪 ===")

result1 = agent.invoke(
    {"messages": [{"role": "user", "content": "幫我算 100 * 25"}]},
    config=config,
)

for msg in result1["messages"]:
    if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
        print(f"AI: {msg.content}")

# 第二輪對話 — Agent 記得之前算過什麼
print("\n=== 第二輪 ===")

result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "把剛才的結果除以 5"}]},
    config=config,  # 使用相同的 thread_id
)

for msg in result2["messages"]:
    if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
        print(f"AI: {msg.content}")

# 第三輪 — 繼續基於之前的對話
print("\n=== 第三輪 ===")

result3 = agent.invoke(
    {"messages": [{"role": "user", "content": "再加上 50 呢？"}]},
    config=config,
)

for msg in result3["messages"]:
    if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
        print(f"AI: {msg.content}")
