# ch03/max_tokens.py

"""
示範 max_tokens 參數
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# 限制最多輸出 50 個 Token（大約 15-25 個中文字）
model_short = init_chat_model(
    "google_genai:gemini-2.5-flash",
    max_tokens=50
)

response = model_short.invoke("請詳細介紹台灣的歷史。")

print(f"回應：{response.content}")
print(f"（注意：回答可能在中途被截斷）")
