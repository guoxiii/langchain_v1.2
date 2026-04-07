# interceptor_context.py

"""使用 Interceptor 注入使用者上下文"""
import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent


@dataclass
class UserContext:
    """定義使用者上下文的資料結構"""
    user_id: str
    language: str

async def inject_user_context(
    request: MCPToolCallRequest,
    handler,
):

    """將使用者資訊注入到工具呼叫中。"""
    # 從 LangGraph 的 runtime context 取得使用者資訊
    runtime = request.runtime

    if runtime and runtime.context:
        user_id = runtime.context.user_id
        language = runtime.context.language

        # 修改工具呼叫的參數，加入使用者資訊
        modified_request = request.override(
            args={
                **request.args,
                "user_id": user_id,
                "language": language,
            }
        )

        return await handler(modified_request)

    return await handler(request)

async def main():
    client = MultiServerMCPClient(
        {
            "my_service": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        tool_interceptors=[inject_user_context],
    )

    tools = await client.get_tools()

    # 看看 LLM 看到的工具 schema 長什麼樣
    # for t in tools:
    #    print(f"Schema: {t.args_schema}")

    # 建立 Agent，指定 context_schema
    agent = create_agent(
        "google_genai:gemini-2.5-flash",
        tools,
        context_schema=UserContext,
        system_prompt = ("你是一個訂單查詢助手，使用者的身分資訊(user_id、language)會由系統自動注入，不需要向使用者詢問這些資訊，直接呼叫工具即可。")
    )

    # 呼叫時傳入使用者上下文
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "查詢我的訂單"}]},
        context={"user_id": "user_123", "language": "zh-TW"},
    )

    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
