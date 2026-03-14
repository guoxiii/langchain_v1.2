# auth_headers_example.py

"""使用 HTTP Headers 進行認證"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    client = MultiServerMCPClient(
        {
            "secure_service": {
                "transport": "http",
                "url": "https://api.example.com/mcp",
                "headers": {
                    "Authorization": "Bearer YOUR_API_TOKEN",
                    "X-Custom-Header": "custom-value",
                },
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent("google_genai:gemini-2.5-flash", tools)

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "查詢資料"}]}
    )

if __name__ == "__main__":
    asyncio.run(main())