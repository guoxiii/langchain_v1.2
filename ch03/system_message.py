# ch03/system_message.py

"""
示範 SystemMessage 的效果
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# 不帶 SystemMessage 的回答
response_no_system = model.invoke([
    HumanMessage("什麼是遞迴？")
])

print("【無角色設定】")
print(response_no_system.content)
print("---")

# 帶 SystemMessage 的回答
response_with_system = model.invoke([
    SystemMessage("你是一位幼兒園老師，擅長用說故事的方式解釋複雜概念，請用小朋友聽得懂的方式回答。"),
    HumanMessage("什麼是遞迴？")
])

print("【幼兒園老師角色】")
print(response_with_system.content)
