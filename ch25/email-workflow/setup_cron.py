# setup_cron.py

"""設定 Cron Job — 讓工作流每天自動跑"""

import asyncio
from langgraph_sdk import get_client

async def setup_daily_cron():
    client = get_client(url="http://localhost:2024")

    # 建立每天早上 9 點（UTC+8 的 1:00 AM UTC）執行的 Cron Job
    cron_job = await client.crons.create(
        assistant_id="email_workflow",
        schedule="0 1 * * *",  # 每天 UTC 01:00 = 台灣 09:00

        input={
            "messages": [
                {
                    "role": "user",
                    "content": "開始今日郵件處理流程",
                }
            ]
        },
    )

    print(f"✅ Cron Job 已建立！")
    print(f"   排程：每天台灣時間 09:00")
    print(f"   Job ID：{cron_job['cron_id']}")
    print(f"\n⚠️ 提醒：Cron 排程使用 UTC 時區！")
    print(f"   台灣時間 09:00 = UTC 01:00")

    return cron_job

async def list_cron_jobs():
    """列出所有已設定的 Cron Job"""
    client = get_client(url="http://localhost:2024")
    jobs = await client.crons.search()
    print(f"\n📋 現有 Cron Job 列表：")

    for job in jobs:
        print(f"   - ID: {job['cron_id']}")
        print(f"     排程: {job['schedule']}")
        print(f"     助手: {job['assistant_id']}")
        print()

async def delete_cron_job(cron_id: str):
    """刪除 Cron Job — 記得不用的時候要刪掉，不然會一直跑！"""
    client = get_client(url="http://localhost:2024")
    await client.crons.delete(cron_id)
    print(f"🗑️ Cron Job {cron_id} 已刪除")

if __name__ == "__main__":
    asyncio.run(setup_daily_cron())
