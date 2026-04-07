# background_run.py

"""背景執行範例：讓 Agent 在幕後完成長時間任務"""

import asyncio
import time
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")

    # 建立 Thread
    thread = await client.threads.create()
    thread_id = thread["thread_id"]

    # 提交背景任務
    print("📤 提交背景任務...")

    run = await client.runs.create(
        thread_id,
        "my_agent",
        input={
            "messages": [
                {
                    "role": "human",
                    "content": "請詳細搜尋並分析 2026 年全球 AI 產業的五大趨勢，"
                               "每個趨勢都要有具體的數據支撐和案例說明。"
                }
            ]
        },
    )

    run_id = run["run_id"]

    print(f"✅ 任務已提交，Run ID: {run_id}")
    print(f"   初始狀態: {run['status']}")

    # 輪詢等待結果
    print("\n⏳ 等待任務完成...")
    poll_count = 0

    while True:
        poll_count += 1
        run_info = await client.runs.get(thread_id, run_id)
        status = run_info["status"]

        if status == "success":
            print(f"\n🎉 任務完成！（輪詢了 {poll_count} 次）")
            break
        elif status == "error":
            print(f"\n❌ 任務失敗！")
            print(f"   錯誤: {run_info.get('error', '未知錯誤')}")
            return
        else:
            print(f"   [{poll_count}] 狀態: {status}...")
            await asyncio.sleep(2)

    # 取得最終結果
    state = await client.threads.get_state(thread_id)
    messages = state["values"].get("messages", [])
    print("\n📋 Agent 回應：")

    for msg in messages:
        role = msg.get("role", msg.get("type", "unknown"))
        content = msg.get("content", "")

        if role in ("ai", "assistant") and content:
            print(f"\n{content[:500]}...")  # 印出前 500 字


if __name__ == "__main__":
    asyncio.run(main())
