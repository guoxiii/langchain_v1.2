"""
檔案：tool_retry_demo.py
ToolRetryMiddleware 用於處理工具執行失敗
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRetryMiddleware,
    ToolRetryMiddleware,
)
from langchain.tools import tool

@tool
def query_database(sql: str) -> str:
    """執行 SQL 查詢"""
    # 模擬資料庫查詢（可能因為連線問題暫時失敗）
    return f"查詢結果：3 筆資料"

@tool
def call_external_api(endpoint: str) -> str:
    """呼叫外部 API"""
    return f"API 回應：成功"

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[query_database, call_external_api],
    middleware=[
        # 模型層級重試
        ModelRetryMiddleware(max_retries=3),
        # 工具層級重試（只針對特定工具）
        ToolRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
            max_delay=60.0,
            jitter=True,
            tools=["call_external_api"],  # 只對外部 API 工具重試
            retry_on=(ConnectionError, TimeoutError),
            on_failure="continue",        # 失敗時回傳錯誤訊息給 Agent
        ),
    ],
)
