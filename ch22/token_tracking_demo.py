"""
檔案：token_tracking_demo.py
追蹤 Token 用量的實用方法
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage

model = init_chat_model("google_genai:gemini-2.5-flash")

response = model.invoke([
    HumanMessage(content="用 100 字解釋什麼是 RAG")
])

# 從 response 的 usage_metadata 取得 Token 統計
if response.usage_metadata:
    usage = response.usage_metadata
    print(f"輸入 Token: {usage.get('input_tokens', 'N/A')}")
    print(f"輸出 Token: {usage.get('output_tokens', 'N/A')}")
    print(f"總計 Token: {usage.get('total_tokens', 'N/A')}")

    # 如果有快取命中資訊
    if "cache_read_input_tokens" in usage:
        print(f"快取命中 Token: {usage['cache_read_input_tokens']}")
