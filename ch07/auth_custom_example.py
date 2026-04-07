# auth_custom_example.py

"""使用 httpx.Auth 自定義認證"""
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

class MyCustomAuth(httpx.Auth):
    """自定義的認證類別。
    這裡示範一個簡單的 Token refresh 機制。
    """
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request):
        # 在每個請求中加入 Authorization 標頭
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

async def main():
    # 使用自定義的 Auth
    auth = MyCustomAuth(token="your_token_here")

    client = MultiServerMCPClient(
        {
            "secure_service": {
                "transport": "http",
                "url": "https://api.example.com/mcp",
                "auth": auth,
            }
        }
    )

    tools = await client.get_tools()
    agent = create_agent("google_genai:gemini-2.5-flash", tools)
    # ... 使用 agent

if __name__ == "__main__":
    asyncio.run(main())