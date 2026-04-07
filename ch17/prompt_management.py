# ch17/prompt_management.py

"""使用 LangSmith Prompt Hub 管理 Prompt"""

from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# 初始化 LangSmith Client
client = Client()

# ========== 建立並推送 Prompt ==========
# 建立一個 ChatPromptTemplate
customer_service_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一個專業的客服助手。回覆要簡潔有禮，"
            "如果不確定答案，請誠實告知使用者。"
            "使用者的名字是 {user_name}。",
        ),
        ("human", "{question}"),
    ]
)

# 推送到 LangSmith Hub
client.push_prompt(
    "customer-service-v1",     #為這一個版本的prompt取一個名稱
    object=customer_service_prompt,
    description="客服助手的 System Prompt，第一版",
    is_public=False,  # 設為私有
)

print("✅ Prompt 已推送到 LangSmith Hub")

# ========== 從 Hub 拉取 Prompt ==========
# 拉取最新版本

prompt = client.pull_prompt("customer-service-v1")
print(f"✅ 已拉取 Prompt：{type(prompt)}")

# 使用拉取的 prompt
formatted = prompt.invoke(
    {"user_name": "小明", "question": "我的訂單什麼時候會到？"}
)

print(f"格式化結果：{formatted}")
