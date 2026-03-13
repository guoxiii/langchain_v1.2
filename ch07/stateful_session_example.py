# stateful_session_example.py

"""有狀態的 MCP Session 示範"""
import asyncio

from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

async def main():
    client = MultiServerMCPClient(
        {
            "database": {
                "transport": "stdio",
                "command": "python",
                "args": ["/path/to/database_server.py"],
            }
        }
    )

    # 開啟有狀態的 Session
    # 在這個 async with 區塊內，所有工具呼叫都共用同一個 Session
    async with client.session("database") as session:
        # 從這個 Session 載入工具
        tools = await load_mcp_tools(session)

        agent = create_agent(
            "google_genai:gemini-2.5-flash",
            tools,
        )

        # 第一次呼叫：建立資料表
        await agent.ainvoke(
            {"messages": [{"role": "user", "content": "建立一個 users 資料表"}]}
        )

        # 第二次呼叫：Server 還記得之前建立的資料表
        await agent.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": "在 users 表中插入一筆資料"}
                ]
            }
        )

    # Session 在這裡自動關閉

if __name__ == "__main__":
    asyncio.run(main())
