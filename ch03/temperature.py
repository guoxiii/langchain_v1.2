# ch03/temperature.py

"""
示範溫度參數對回答的影響
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
question = "幫我想一個科幻小說的書名。"

# 低溫度：回答穩定、可預測
model_low = init_chat_model("google_genai:gemini-2.5-flash", temperature=0)

# 高溫度：回答有創意、每次不同
model_high = init_chat_model("google_genai:gemini-2.5-flash", temperature=1.0)

print("【溫度 = 0（穩定模式）】")

for i in range(3):
    response = model_low.invoke(question)
    print(f"  第 {i+1} 次：{response.content}")

print()
print("【溫度 = 1.0（創意模式）】")

for i in range(3):
    response = model_high.invoke(question)
    print(f"  第 {i+1} 次：{response.content}")
