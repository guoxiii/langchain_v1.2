# load_tools_example.py

"""使用 load_mcp_tools 直接載入工具"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

async def main():
    # 直接使用 MCP SDK 的 Client 連接
    async with streamable_http_client("http://localhost:8000/mcp") as (
        read,
        write,
        _,
    ):

        async with ClientSession(read, write) as session:
            # 初始化連線
            await session.initialize()
            # 用 load_mcp_tools 把 MCP 工具轉成 LangChain 工具
            tools = await load_mcp_tools(session)

            # 建立 Agent 並使用
            agent = create_agent(
                "google_genai:gemini-2.5-flash",
                tools,
            )

            response = await agent.ainvoke(
                {
                    "messages": [
                        {"role": "user", "content": "Tokyo 的天氣如何？"}
                    ]
                }
            )

            for msg in response["messages"]:
                print(f"[{msg.type}] {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
