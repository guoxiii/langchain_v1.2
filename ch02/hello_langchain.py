"""
第一個 LangChain 程式 — Hello Gemini!
驗證開發環境是否正確設定。
"""
import os

# Step 1：載入環境變數
from dotenv import load_dotenv
load_dotenv()


# Step 2：確認 API Key 已設定
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ 錯誤：請在 .env 檔案中設定 GOOGLE_API_KEY")
    print("   取得方式：https://aistudio.google.com/")
    exit(1)

# Step 3：使用 init_chat_model 初始化模型
from langchain.chat_models import init_chat_model
model = init_chat_model("google_genai:gemini-2.5-flash")

# Step 4：發送訊息給模型
response = model.invoke("你好！請用一句話介紹你自己。")

# Step 5：顯示回應
print("🤖 Gemini 回應：")
print(response.content)
