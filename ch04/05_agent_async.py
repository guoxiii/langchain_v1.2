import asyncio
import os
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

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_weather],
)

async def main():
    # ainvoke：非同步等待完整結果

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "台北天氣？"}]}
    )

    print("ainvoke 結果：")

    for msg in result["messages"]:
        if msg.type == "ai" and msg.content:
            print(f"  {msg.content}")

    print("\n" + "="*60)

    # astream：非同步串流
    print("\nastream 逐步輸出：")

    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "東京天氣？"}]},
        stream_mode="updates",
    ):

        for node_name, updates in chunk.items():
            print(f"  [{node_name}]", end=" ")

            if "messages" in updates:
                for msg in updates["messages"]:
                    if msg.content:
                        print(msg.content[:80])

# 執行非同步函式
asyncio.run(main())
