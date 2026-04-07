# cron_demo.py

# Cron Jobs 是 LangGraph Platform（雲端）專屬功能，本地開發伺服器（langgraph dev）雖然有 /crons endpoint，但背後的排程器必須要啟動，否則程式執行會發生錯誤。

"""Cron Jobs 排程執行範例"""

import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")

    # ===== 有狀態的 Cron Job =====
    # 綁定到特定 Thread，每次執行都會延續之前的對話歷史
    thread = await client.threads.create(
        metadata={"purpose": "daily-report"}
    )

    cron_stateful = await client.crons.create_for_thread(
        thread["thread_id"],
        "my_agent",
        schedule="0 8 * * *",  # 每天 UTC 早上 8 點
        input={
            "messages": [
                {
                    "role": "human",
                    "content": "請整理今天的銷售數據摘要，"
                               "並與昨天的數據做比較。"
                }
            ]
        },
    )

    print(f"✅ 有狀態 Cron Job 建立完成")
    print(f"   Cron ID: {cron_stateful['cron_id']}")
    print(f"   綁定 Thread: {thread['thread_id']}")
    print(f"   排程: 每天 UTC 08:00")

    # ===== 無狀態的 Cron Job =====
    # 每次執行都建立新的 Thread（獨立的對話）
    cron_stateless = await client.crons.create(
        "my_agent",
        schedule="0 20 * * 5",  # 每週五 UTC 晚上 8 點
        input={
            "messages": [
                {
                    "role": "human",
                    "content": "請生成本週的工作週報。"
                }
            ]
        },
    )

    print(f"\n✅ 無狀態 Cron Job 建立完成")
    print(f"   Cron ID: {cron_stateless['cron_id']}")
    print(f"   排程: 每週五 UTC 20:00")

    # ===== 列出所有 Cron Jobs =====
    crons = await client.crons.search()
    print(f"\n目前的 Cron Jobs: {len(crons)} 個")

    for c in crons:
        print(f"  - {c['cron_id']}: {c['schedule']}")

    # ===== 刪除 Cron Job =====
    # 重要！用完記得刪，不然會一直執行（一直花 API 費用 💸）
    await client.crons.delete(cron_stateful["cron_id"])
    print(f"\n🗑️ 已刪除 Cron Job: {cron_stateful['cron_id']}")

if __name__ == "__main__":
    asyncio.run(main())
