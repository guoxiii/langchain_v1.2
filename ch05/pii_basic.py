# 檔案：ch05/pii_basic.py

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

load_dotenv()

# === 沒有 Middleware 的 Agent ===
agent_no_pii = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
)

# === 有 PII Middleware 的 Agent ===
agent_with_pii = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)

user_msg = (
    "請幫我整理以下客戶資料成表格：\n"
    "姓名：王小明\n"
    "Email：wang.ming@example.com\n"
    "信用卡：4532-1234-5678-9012\n"
    "訂單編號：ORD-20250601"
)

print("=== 無 Middleware ===")
r1 = agent_no_pii.invoke(
    {"messages": [{"role": "user", "content": user_msg}]}
)
print(r1["messages"][-1].content)

print("\n=== 有 PII Middleware ===")
r2 = agent_with_pii.invoke(
    {"messages": [{"role": "user", "content": user_msg}]}
)
print(r2["messages"][-1].content)