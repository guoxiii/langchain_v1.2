# agent.py
"""整合三個 MCP Server 的完整 Agent"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.agents import create_agent

# === Interceptor：記錄所有工具呼叫 ===
async def logging_interceptor(
    request: MCPToolCallRequest,
    handler,
):

    """記錄所有 MCP 工具呼叫的攔截器。"""
    print(f"\n  🔧 [MCP] 呼叫工具: {request.server_name}/{request.name}")
    print(f"     參數: {request.args}")
    result = await handler(request)
    print(f"  ✅ [MCP] 完成: {request.server_name}/{request.name}")

    return result

async def main():
    # 取得目前腳本所在的目錄，用來建立絕對路徑
    base_dir = os.path.dirname(os.path.abspath(__file__))
    servers_dir = os.path.join(base_dir, "servers")
    
    # === 建立 MultiServerMCPClient，連接三個 Server ===
    client = MultiServerMCPClient(
        {
            # 計算器 Server（stdio 傳輸）
            "calculator": {
                "transport": "stdio",
                "command": "python",
                "args": [os.path.join(servers_dir, "calculator_server.py")],
            },

            # 天氣 Server（HTTP 傳輸）
            # ⚠️ 請先在另一個終端機啟動：python servers/weather_server.py
            "weather": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },

            # 筆記 Server（stdio 傳輸）
            "notes": {
                "transport": "stdio",
                "command": "python",
                "args": [os.path.join(servers_dir, "notes_server.py")],
            },
        },
        tool_interceptors=[logging_interceptor],
    )

    # 取得所有工具
    tools = await client.get_tools()

    print("=" * 60)
    print("🤖 MCP Agent 已就緒！")
    print(f"   已載入 {len(tools)} 個工具：")

    for tool in tools:
        print(f"   - {tool.name}")

    print("=" * 60)

    # 建立 Agent
    agent = create_agent(
        "anthropic:claude-sonnet-4-6",
        tools,
        system_prompt="你是一個智慧助理，可以進行數學計算、查詢天氣、以及管理筆記。"
        "請用繁體中文回答使用者的問題。"
        "當使用者詢問時，善用你擁有的工具來提供最好的回答。",
    )

    # === 互動式對話迴圈 ===
    print("\n💬 開始對話（輸入 'quit' 結束）：\n")

    while True:
        user_input = input("你：")

        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 再見！")
            break

        if not user_input.strip():
            continue
        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]}
            )

            # 找到最後一則 AI 回覆
            ai_messages = [
                msg
                for msg in response["messages"]
                if msg.type == "ai" and msg.content
            ]

            if ai_messages:
                print(f"\n🤖 助理：{ai_messages[-1].content}\n")
            else:
                print("\n🤖 助理：（沒有回覆）\n")
        except Exception as e:
            print(f"\n❌ 發生錯誤：{e}\n")

if __name__ == "__main__":
    asyncio.run(main())
