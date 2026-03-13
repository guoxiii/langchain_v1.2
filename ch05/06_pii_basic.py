# 檔案：ch05/06_pii_basic.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[
        # 遮蔽 Email 地址
        PIIMiddleware("email", strategy="redact", apply_to_input=True),

        # 遮蔽信用卡號碼
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "我的 Email 是 john@example.com，信用卡號是 4532-1234-5678-9012"}]}
)

print(result["messages"][-1].content)
