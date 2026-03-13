# 檔案：ch05/10_model_retry.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],

    middleware=[
        ModelRetryMiddleware(
            max_retries=3,        # 最多重試 3 次
            backoff_factor=2.0,   # 退避倍數
            initial_delay=1.0,    # 初始等待秒數
        ),
    ],
)
