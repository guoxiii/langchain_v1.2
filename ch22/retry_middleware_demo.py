"""
檔案：retry_middleware_demo.py
ModelRetryMiddleware 完整使用範例
"""
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware
from langchain.tools import tool

@tool
def get_stock_price(symbol: str) -> str:
    """查詢股票即時價格"""
    # 模擬 API 呼叫
    return f"{symbol} 目前股價: NT$150.5"

# 基本用法：使用預設設定（2 次重試，指數退避）
basic_agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_stock_price],
    middleware=[ModelRetryMiddleware()],
)

# 進階用法：自訂重試策略
def should_retry(error: Exception) -> bool:
    """自訂重試條件：只在特定錯誤時重試"""
    # Rate Limiting（429）和伺服器錯誤（5xx）值得重試

    if hasattr(error, "status_code"):
        return error.status_code in (429, 500, 502, 503)

    # 網路逾時也值得重試
    if isinstance(error, (TimeoutError, ConnectionError)):
        return True

    # 其他錯誤不重試（例如認證失敗、參數錯誤）
    return False

advanced_agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[get_stock_price],
    middleware=[
        ModelRetryMiddleware(
            max_retries=4,           # 最多重試 4 次
            backoff_factor=2.0,      # 指數退避因子（等待時間翻倍）
            initial_delay=1.0,       # 初次重試等 1 秒
            max_delay=60.0,          # 最長等待 60 秒
            jitter=True,             # 加入隨機抖動，避免同時重試造成「驚群效應」
            retry_on=should_retry,   # 自訂重試條件函式
            on_failure="continue",   # 重試耗盡後回傳錯誤訊息（而非拋出例外）
        ),
    ],
)
