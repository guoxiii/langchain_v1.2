# ch03/all_params.py

"""
示範 init_chat_model 的各種參數設定
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0.7,		# 溫度
    max_tokens=1024,		# 最大輸出 Token 數
    max_retries=3,		# 失敗重試次數（網路錯誤、速率限制等）
)

response = model.invoke("請推薦三個台南的景點。")
print(response.content)
