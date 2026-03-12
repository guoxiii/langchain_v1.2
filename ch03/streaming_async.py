# ch03/streaming_async.py

"""
示範非同步串流輸出
"""

import asyncio
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

async def main():
    model = init_chat_model("google_genai:gemini-2.5-flash")
    

    print("AI 正在回答：", end="", flush=True)    

    # astream() 回傳一個 async generator
    async for chunk in model.astream("請推薦三本 Python 入門書籍。"):
        print(chunk.content, end="", flush=True)    

    print()

# 執行非同步函式
asyncio.run(main())
