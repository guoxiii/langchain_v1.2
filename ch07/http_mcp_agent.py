# http_mcp_agent.py

"""連接 HTTP 傳輸的 MCP Server"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


async def main():
    # 連接到 HTTP 傳輸的天氣 Server
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    tools = await client.get_tools()

    agent = create_agent(
        "google_genai:gemini-2.5-flash",
        tools,
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "台北現在的天氣如何？"}]}
    )

    for msg in response["messages"]:
        print(f"[{msg.type}] {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
