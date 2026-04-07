# test_rag_agent.py

"""RAG Agent 部署測試腳本"""

import asyncio
from langgraph_sdk import get_client


async def test_basic_qa():
    """測試基本問答功能"""
    client = get_client(url="http://localhost:2024")
    thread = await client.threads.create()

    print("🧪 測試 1：基本問答")
    print("-" * 50)

    async for chunk in client.runs.stream(
        thread["thread_id"],
        "rag_agent",
        input={
            "messages": [
                {"role": "human", "content": "什麼是 RAG？它的流程是什麼？"}
            ]
        },
        stream_mode="messages-tuple",
    ):
        if chunk.event == "messages":
            msg, metadata = chunk.data

            # 只處理 AI 的串流回覆
            if msg["type"] != "AIMessageChunk":
                continue

            content = msg.get("content")
            if not content:
                continue

            # content 可能是字串（Google Genai）或 list of blocks（Anthropic）
            if isinstance(content, str):
                print(content, end="", flush=True)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        print(block["text"], end="", flush=True)

    print("\n")


async def test_multi_turn():
    """測試多輪對話"""
    client = get_client(url="http://localhost:2024")
    thread = await client.threads.create()

    print("🧪 測試 2：多輪對話")
    print("-" * 50)

    # 第一輪
    await client.runs.wait(
        thread["thread_id"],
        "rag_agent",
        input={
            "messages": [
                {"role": "human", "content": "LangGraph Platform 是什麼？"}
            ]
        },
    )

    print("  ✅ 第一輪完成")

    # 第二輪（延續對話）
    result = await client.runs.wait(
        thread["thread_id"],
        "rag_agent",
        input={
            "messages": [
                {"role": "human", "content": "它取代了什麼工具？為什麼？"}
            ]
        },
    )

    print("  ✅ 第二輪完成（Agent 應該記得上一輪的對話）")

    # 驗證狀態
    state = await client.threads.get_state(thread["thread_id"])
    msg_count = len(state["values"].get("messages", []))
    print(f"  📊 Thread 中共有 {msg_count} 則訊息")


async def main():
    print("=" * 60)
    print("  RAG Agent 部署測試")
    print("=" * 60)
    print()

    await test_basic_qa()
    await test_multi_turn()

    print("\n" + "=" * 60)
    print("  🎉 所有測試通過！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())