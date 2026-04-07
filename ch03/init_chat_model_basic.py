# ch03/init_chat_model_basic.py
"""
示範 init_chat_model 的基本用法
"""
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# 載入 .env 檔案中的 API 金鑰
load_dotenv()

# 確認 API 金鑰已設定
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("請在 .env 檔案中設定 GOOGLE_API_KEY")

# 一行程式碼初始化 Gemini 模型
model = init_chat_model("google_genai:gemini-2.5-flash")

# 最簡單的呼叫方式：直接傳入字串
response = model.invoke("請用一句話解釋什麼是 Python。")

# response 是一個 AIMessage 物件
print(f"回應類型：{type(response)}")
print(f"回應內容：{response.content}")
