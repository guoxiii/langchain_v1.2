# 檔案：ch05/summarization.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],

    middleware=[
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash",  # 用來做摘要的模型
            trigger=("tokens", 4000),  # 當 Token 數超過 4000 時觸發摘要
            keep=("messages", 20),     # 保留最近 20 則訊息不被摘要
        ),
    ],
)
