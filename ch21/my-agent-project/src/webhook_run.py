# webhook_run.py

"""使用 Webhook 接收背景任務完成通知"""

import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")
    thread = await client.threads.create()

    # 提交任務並指定 Webhook URL
    run = await client.runs.create(
        thread["thread_id"],
        "my_agent",
        input={
            "messages": [
                {"role": "human", "content": "幫我分析今天的新聞摘要"}
            ]
        },
        webhook="https://your-server.com/api/agent-callback",
    )

    print(f"任務已提交，完成後會通知 Webhook")
    print(f"Run ID: {run['run_id']}")

if __name__ == "__main__":
    asyncio.run(main())
