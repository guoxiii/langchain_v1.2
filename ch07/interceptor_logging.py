# interceptor_logging.py

"""使用 Interceptor 記錄所有 MCP 工具呼叫"""
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent

async def logging_interceptor(
    request: MCPToolCallRequest,
    handler,
):

    """記錄每次 MCP 工具呼叫的攔截器。"""
    print(f"🔧 呼叫工具: {request.name}")
    print(f"   參數: {request.args}")
    print(f"   Server: {request.server_name}")

    start_time = time.time()

    # 呼叫下一層（可能是另一個 Interceptor，或是實際的工具執行）
    result = await handler(request)
    elapsed = time.time() - start_time

    print(f"✅ 完成: {request.name}（耗時 {elapsed:.2f}s）")

    return result

async def main():
    client = MultiServerMCPClient(
        {
            "calculator": {
                "transport": "stdio",
                "command": "python",
                "args": ["/path/to/calculator_server.py"],
            },
        },

        # 在這裡設定 Interceptor
        tool_interceptors=[logging_interceptor],
    )

    tools = await client.get_tools()
    agent = create_agent("google_genai:gemini-2.5-flash", tools)

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "計算 42 + 58"}]}
    )

    for msg in response["messages"]:
        if hasattr(msg, "content"):
            print(f"[{msg.type}] {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())