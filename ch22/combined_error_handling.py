"""
檔案：combined_error_handling.py
組合多種錯誤處理 Middleware 的生產級配置
"""
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRetryMiddleware,
    ModelFallbackMiddleware,
    ToolRetryMiddleware,
    ToolCallLimitMiddleware,
    SummarizationMiddleware,
)
from langchain.tools import tool

@tool
def search_documents(query: str) -> str:
    """搜尋內部文件"""
    return f"找到相關文件..."

@tool
def query_api(endpoint: str) -> str:
    """呼叫外部 API"""
    return f"API 回應成功"

# 生產級 Agent：多層防禦
production_agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[search_documents, query_api],
    system_prompt="你是企業 AI 助理，用繁體中文回答。",
    middleware=[
        # 第 1 層：對話歷史摘要（避免 Context Window 溢出）
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash",
            trigger=[("tokens", 8000), ("messages", 30)],
            keep=("messages", 8),
        ),
        # 第 2 層：模型自動重試（處理暫時性 API 故障）
        ModelRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            jitter=True,
        ),
        # 第 3 層：模型降級（主模型持續失敗時切換備援）
        ModelFallbackMiddleware(
            "anthropic:claude-sonnet-4-6",
        ),
        # 第 4 層：工具重試（外部 API 呼叫重試）
        ToolRetryMiddleware(
            max_retries=2,
            tools=["query_api"],
            on_failure="continue",
        ),
        # 第 5 層：工具呼叫次數限制（防止無限迴圈）
        ToolCallLimitMiddleware(run_limit=15),
    ],
)