# ch03/streaming_basic.py

"""
示範基本的串流輸出
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

print("AI 正在回答：", end="", flush=True)

# stream() 回傳一個 generator
for chunk in model.stream("請用 100 字介紹台灣的美食文化。"):
    # chunk 是 AIMessageChunk 物件
    print(chunk.content, end="", flush=True)

print()  # 最後換行
