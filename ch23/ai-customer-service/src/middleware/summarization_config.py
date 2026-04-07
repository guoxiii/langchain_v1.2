# src/middleware/summarization_config.py

"""
對話摘要 Middleware 設定。
自動壓縮過長的對話歷史，防止 Context Window 溢出。
"""

from langchain.agents.middleware import SummarizationMiddleware

def create_summarization_middleware():
    """建立對話摘要 Middleware。"""
    return SummarizationMiddleware(
        # 使用較便宜的模型來做摘要
        model="google_genai:gemini-2.5-flash",
        # 當 token 數超過 4000 時觸發摘要
        trigger=("tokens", 4000),
        # 保留最近 20 則訊息不被摘要
        keep=("messages", 20),
    )
