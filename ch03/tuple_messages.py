# ch03/tuple_messages.py

"""
示範使用 tuple 快捷語法建立訊息
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# 使用 tuple 語法：("角色", "內容")
messages = [
    ("system", "你是一個友善的中文助手。"),
    ("human", "你好！"),
]

response = model.invoke(messages)
print(response.content)
