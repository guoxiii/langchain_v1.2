# multi_server_agent.py

"""同時連接多個 MCP Server 的 Agent"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    # 同時連接計算器（stdio）和天氣（HTTP）兩個 Server
    client = MultiServerMCPClient(
        {
            "calculator": {
                "transport": "stdio",
                "command": "python",
                "args": ["/absolute/path/to/calculator_server.py"],
            },
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        }
    )

    # get_tools() 會收集所有 Server 的工具，合併成一個列表
    tools = await client.get_tools()

    print(f"總共取得 {len(tools)} 個工具：")

    for tool in tools:
        print(f"  - {tool.name}")

    # 建立 Agent
    agent = create_agent(
        "google_genai:gemini-2.5-flash",
        tools,
    )

    # Agent 可以同時使用來自不同 Server 的工具
    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "台北現在幾度？如果溫度乘以 2 是多少？",
                }
            ]
        }
    )

    for msg in response["messages"]:
        print(f"[{msg.type}] {msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
