# ch08/toolnode_error.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool
from langgraph.prebuilt import ToolNode

@tool

def unreliable_api(query: str) -> str:
    """呼叫一個不太穩定的外部 API。

    Args:
        query: 查詢內容
    """
    import random

    if random.random() < 0.3:  # 30% 機率失敗
        raise ValueError("API 暫時無法使用，請稍後再試")

    return f"API 回傳結果：{query} 的相關資訊"

@tool
def stable_tool(text: str) -> str:
    """一個穩定的工具。

    Args:
        text: 輸入文字
    """
    return f"處理結果：{text}"

# 方式一：捕捉所有錯誤，回傳錯誤訊息給 LLM
tool_node = ToolNode(
    tools=[unreliable_api, stable_tool],
    handle_tool_errors=True
)

# 方式二：自訂錯誤訊息
tool_node = ToolNode(
    tools=[unreliable_api, stable_tool],
    handle_tool_errors="工具執行失敗，請嘗試其他方式或稍後重試。"
)

# 方式三：自訂錯誤處理函式
def global_error_handler(e: Exception) -> str:
    if isinstance(e, ValueError):
        return f"外部服務暫時不可用：{e}。建議稍後重試。"

    return f"發生未預期的錯誤：{type(e).__name__}: {e}"

tool_node = ToolNode(
    tools=[unreliable_api, stable_tool],
    handle_tool_errors=global_error_handler
)

# 方式四：只捕捉特定類型的例外
tool_node = ToolNode(
    tools=[unreliable_api, stable_tool],
    handle_tool_errors=(ValueError, TimeoutError)
)
