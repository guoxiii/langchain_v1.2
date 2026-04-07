# 檔案：ch05/moderation.py

from dotenv import load_dotenv
from langchain_openai.middleware import OpenAIModerationMiddleware
from langchain.agents import create_agent

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",  # 主模型用 Gemini
    tools=[],

    middleware=[
        OpenAIModerationMiddleware(
            model="omni-moderation-latest",  # OpenAI 的內容審查模型
            check_input=True,     # 檢查使用者輸入
            check_output=True,    # 檢查模型輸出
            exit_behavior="end",  # 違規時結束對話
        ),
    ],
)