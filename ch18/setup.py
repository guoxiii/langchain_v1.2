# setup.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

# 建立 LangSmith Client（評估操作的核心入口）
ls_client = Client()

print("✅ LangSmith Client 初始化完成")
print(f"📊 API URL：{ls_client.api_url}")