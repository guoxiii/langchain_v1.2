# test_client_sync.py

"""同步版本的 LangGraph SDK 客戶端"""

from langgraph_sdk import get_sync_client

def main():
    client = get_sync_client(url="http://localhost:2024")

    # 建立 Thread
    thread = client.threads.create()

    # 串流回應
    for chunk in client.runs.stream(
        thread["thread_id"],
        "my_agent",
        input={
            "messages": [
                {"role": "human", "content": "幫我算 15% 的小費，帳單是 1280 元"}
            ]
        },
        stream_mode="messages-tuple",
    ):
        print(f"[{chunk.event}] {chunk.data}")

if __name__ == "__main__":
    main()
