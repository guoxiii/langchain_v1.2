# runs_demo.py

"""Runs API — 三種執行模式比較"""

import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    input_data = {
        "messages": [
            {"role": "human", "content": "請幫我搜尋台灣 2026 年的 GDP 成長率"}
        ]
    }

    # ===== 模式一：串流（Streaming）=====
    # 最適合：聊天機器人、即時互動
    # 特點：逐步返回結果，使用者可以看到 Agent 的思考過程

    print("=== 串流模式 ===")

    async for chunk in client.runs.stream(
        thread_id,
        "my_agent",
        input=input_data,
        stream_mode="messages-tuple",  # 逐 Token 串流
    ):

        if chunk.event == "messages":
            print(chunk.data, end="", flush=True)

    print()

    # ===== 模式二：同步等待（Wait）=====
    # 最適合：簡單查詢、30 秒以內的任務
    # 特點：等待完成後一次返回全部結果
    thread2 = await client.threads.create()
    print("\n=== 同步模式 ===")
    result = await client.runs.wait(
        thread2["thread_id"],
        "my_agent",
        input=input_data,
    )

    print(f"完整結果: {result}")

    # ===== 模式三：背景執行（Background）=====
    # 最適合：長時間任務（研究報告、大量資料處理）
    # 特點：立即返回 Run ID，稍後輪詢結果
    thread3 = await client.threads.create()
    print("\n=== 背景模式 ===")

    run = await client.runs.create(
        thread3["thread_id"],
        "my_agent",
        input=input_data,
    )

    print(f"Run 已建立: {run['run_id']}")
    print(f"狀態: {run['status']}")  # "pending" 或 "running"

    # 輪詢等待完成
    import time

    while True:
        run_status = await client.runs.get(
            thread3["thread_id"],
            run["run_id"]
        )

        print(f"  目前狀態: {run_status['status']}")

        if run_status["status"] in ("success", "error"):
            break

        time.sleep(1)
    print(f"最終結果: {run_status}")

if __name__ == "__main__":
    asyncio.run(main())
