# basic_mcp_agent.py

"""基本的 MCP Agent — 連接單一 MCP Server"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    # 建立 MCP Client，連接到計算器 Server（stdio 傳輸）
    client = MultiServerMCPClient(
        {
            "calculator": {
                "transport": "stdio",
                "command": "python",
                "args": ["calculator_server.py"],  # 請替換成完整的絕對路徑
            }
        }
    )

    # 從 MCP Server 取得工具，並轉換成 LangChain 格式
    tools = await client.get_tools()

    # 看看取得了哪些工具
    print("取得的工具：")

    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

    # 建立 Agent（使用 Gemini）
    agent = create_agent(
        "google_genai:gemini-2.5-flash",
        tools,
    )

    # 讓 Agent 使用計算器工具
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "請幫我計算 (15 + 27) × 3"}]}
    )

    # 印出結果
    for msg in response["messages"]:
        print(f"[{msg.type}] {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
