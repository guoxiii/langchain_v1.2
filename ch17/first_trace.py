# ch17/first_trace.py

"""第一個 LangSmith 追蹤範例"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# 載入 .env 檔案中的環境變數
load_dotenv()

# 初始化 Chat Model
llm = init_chat_model("google_genai:gemini-2.5-flash")

# 發送一個簡單的訊息
response = llm.invoke("用一句話解釋什麼是可觀測性（Observability）")

print(response.text)