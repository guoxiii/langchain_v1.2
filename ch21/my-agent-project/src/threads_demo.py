# threads_demo.py

"""Threads API 操作範例"""

import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")
    # 建立 Thread
    thread = await client.threads.create(
        metadata={"user_id": "user-123", "session": "morning"}
    )

    thread_id = thread["thread_id"]
    print(f"建立 Thread: {thread_id}")

    # 在 Thread 上執行 Agent
    result = await client.runs.wait(
        thread_id,
        "my_agent",
        input={
            "messages": [
                {"role": "human", "content": "你好，請自我介紹"}
            ]
        },
    )

    print(f"Agent 回應: {result}")

    # 查看 Thread 的狀態
    state = await client.threads.get_state(thread_id)

    print(f"\nThread 狀態:")
    print(f"  訊息數: {len(state['values'].get('messages', []))}")

    # 查看 Thread 的歷史（所有 Checkpoint）
    history = await client.threads.get_history(thread_id)
    print(f"  Checkpoint 數: {len(history)}")

    # 繼續對話（同一個 Thread）
    result2 = await client.runs.wait(
        thread_id,
        "my_agent",
        input={
            "messages": [
                {"role": "human", "content": "剛才你說了什麼？可以再說一次嗎？"}
            ]
        },
    )

    print(f"\n第二輪回應: {result2}")

    # 搜尋 Threads
    threads = await client.threads.search(
        metadata={"user_id": "user-123"}
    )

    print(f"\nuser-123 的 Threads: {len(threads)} 個")

if __name__ == "__main__":
    asyncio.run(main())
