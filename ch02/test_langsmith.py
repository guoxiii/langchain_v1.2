# test_langsmith.py
import os

from dotenv import load_dotenv
load_dotenv()

tracing = os.getenv("LANGSMITH_TRACING", "false")
api_key = os.getenv("LANGSMITH_API_KEY", "")
project = os.getenv("LANGSMITH_PROJECT", "default")
print(f"追蹤狀態: {'✅ 已啟用' if tracing == 'true' else '❌ 未啟用'}")
print(f"API Key:  {'✅ 已設定' if api_key else '❌ 未設定'}")
print(f"專案名稱: {project}")

if tracing == "true" and not api_key:
    print("\n⚠️ 警告：追蹤已啟用但 API Key 未設定，追蹤資料將無法送出！")
