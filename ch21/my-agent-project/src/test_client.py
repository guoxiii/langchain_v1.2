# test_client.py

"""使用 LangGraph SDK 呼叫本地 Agent 服務"""

import asyncio
from langgraph_sdk import get_client

async def main():
    # 連接到本地開發伺服器
    client = get_client(url="http://localhost:2024")

    # 查看可用的 Assistants
    assistants = await client.assistants.search()
    print("可用的 Assistants：")

    for a in assistants:
        print(f"  - {a['name']} (graph_id: {a['graph_id']})")

    # 建立一個新的對話 Thread
    thread = await client.threads.create()
    print(f"\n建立 Thread: {thread['thread_id']}")

    # 發送訊息並串流接收回應
    print("\n--- Agent 回應 ---")

    async for chunk in client.runs.stream(
        thread["thread_id"],
        "my_agent",  # assistant_id（對應 langgraph.json 中的 graph 名稱）
        input={
            "messages": [
                {"role": "human", "content": "台北到高雄的距離大約幾公里？"}
            ]
        },
        stream_mode="messages-tuple",
    ):
        print(f"事件類型: {chunk.event}")

        if hasattr(chunk, 'data'):
            print(f"資料: {chunk.data}")

        print()

if __name__ == "__main__":
    asyncio.run(main())
