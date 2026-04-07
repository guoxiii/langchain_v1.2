import httpx
import json

BASE_URL = "http://localhost:2024"

# 1. 建立 Assistant
assistant = httpx.post(
    f"{BASE_URL}/assistants",
    json={"graph_id": "customer-service"}
).json()

assistant_id = assistant["assistant_id"]

print(f"✅ Assistant ID: {assistant_id}")

# 2. 建立 Thread
thread = httpx.post(f"{BASE_URL}/threads", json={}).json()
thread_id = thread["thread_id"]

print(f"✅ Thread ID: {thread_id}")

# 3. 發送訊息並等待結果
response = httpx.post(
    f"{BASE_URL}/threads/{thread_id}/runs/wait",
    json={
        "assistant_id": assistant_id,
        "input": {
            "messages": [{"role": "user", "content": "我想退貨"}]
        }
    },
    timeout=60.0
)

print(json.dumps(response.json(), ensure_ascii=False, indent=2))