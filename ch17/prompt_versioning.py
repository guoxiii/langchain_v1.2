# ch17/prompt_versioning.py

"""Prompt 版本迭代"""

from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

client = Client()

# 第二版：加入更多指示
customer_service_prompt_v2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一個專業的客服助手。請遵守以下原則：\n"
            "1. 回覆要簡潔有禮\n"
            "2. 如果不確定答案，請誠實告知\n"
            "3. 如果問題涉及退款，請引導使用者聯繫退款專線\n"
            "4. 回覆中請稱呼使用者為 {user_name}\n"
            "5. 每次回覆結尾加上「還有其他我能幫助的嗎？」",
        ),
        ("human", "{question}"),
    ]
)

# 推送更新（同名 repo 會建立新版本）
client.push_prompt(
    "customer-service-v1",
    object=customer_service_prompt_v2,
    description="客服助手 V2：加入退款引導和結尾問句",
)

print("✅ Prompt V2 已推送")

# 拉取特定版本（使用 tag 或 commit hash）
# latest_prompt = client.pull_prompt("customer-service-v1:latest")
# tagged_prompt = client.pull_prompt("customer-service-v1:production")
