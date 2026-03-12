# ch03/multi_turn.py

"""
示範多輪對話（對話歷史的管理）
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# 模擬多輪對話
messages = [
    SystemMessage("你是一個友善的中文助手。"),
    HumanMessage("我叫小明，我今年 25 歲。"),
    AIMessage("你好小明！很高興認識你。25 歲正是充滿活力的年紀呢！有什麼我可以幫助你的嗎？"),
    HumanMessage("我叫什麼名字？幾歲？"),
]

response = model.invoke(messages)

print(response.content)

# 模型會記得：你叫小明，25 歲
