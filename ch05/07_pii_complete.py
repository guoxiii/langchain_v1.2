# 檔案：ch05/07_pii_complete.py

import os
import re
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.messages import HumanMessage

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],

    middleware=[
        # 內建偵測器：Email
        PIIMiddleware("email", strategy="redact", apply_to_input=True),

        # 內建偵測器：信用卡
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),

        # 自訂偵測器：台灣手機號碼
        PIIMiddleware(
            "phone_tw",
            detector=r"09\d{2}-?\d{3}-?\d{3}",
            strategy="redact",
            apply_to_input=True,
        ),

        # 自訂偵測器：API Key（直接阻擋）
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32,}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

# 測試：包含多種 PII 的訊息
test_message = (
    "我的 Email 是 xiii@example.com，"
    "手機是 0912-345-678，"
    "信用卡號碼是 4532-1234-5678-9012。"
)

print(f"原始訊息：{test_message}")
print()

result = agent.invoke(
    {"messages": [HumanMessage(content=test_message)]}
)

print(f"Agent 回覆：{result['messages'][-1].content}")
