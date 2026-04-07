# error_handling.py
"""API 錯誤處理範例"""
import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")

    try:
        # 嘗試取得不存在的 Thread（使用合法 UUID 格式）
        state = await client.threads.get("00000000-0000-0000-0000-000000000000")
    except Exception as e:
        print(f"Thread 不存在: {e}")

    # 使用 Double Texting 處理
    # 當使用者在 Agent 還沒回完就送出新訊息時
    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    # 第一個 Run（可能還在執行中）
    run1 = await client.runs.create(
        thread_id,
        "my_agent",
        input={"messages": [{"role": "human", "content": "搜尋台灣天氣"}]},
    )

    # 第二個 Run（搶先執行）
    # multitask_strategy 控制衝突處理方式
    run2 = await client.runs.create(
        thread_id,
        "my_agent",
        input={"messages": [{"role": "human", "content": "算了，幫我算數學就好"}]},
        multitask_strategy="enqueue",  # "reject" | "enqueue" | "rollback" | "interrupt"
    )

    print(f"Run 1: {run1['run_id']}")
    print(f"Run 2: {run2['run_id']}")

if __name__ == "__main__":
    asyncio.run(main())