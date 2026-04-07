"""
切換到 Claude 模型 — 只改一行程式碼！
"""

import os

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("ANTHROPIC_API_KEY"):
    print("❌ 錯誤：請在 .env 檔案中設定 ANTHROPIC_API_KEY")
    print("   取得方式：https://console.anthropic.com/")
    exit(1)

from langchain.chat_models import init_chat_model

# 只改這一行！從 google_genai 改成 anthropic
model = init_chat_model("anthropic:claude-sonnet-4-6")

response = model.invoke("你好！請用一句話介紹你自己。")
print("🤖 Claude 回應：")
print(response.content)
