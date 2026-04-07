# ch03/dynamic_model.py

"""
示範如何從環境變數動態選擇模型
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
load_dotenv()

# 從環境變數讀取模型設定，預設使用 Gemini
model_string = os.getenv("LLM_MODEL", "google_genai:gemini-2.5-flash")

print(f"目前使用的模型：{model_string}")

model = init_chat_model(model_string)
response = model.invoke("你好！")

print(response.content)
