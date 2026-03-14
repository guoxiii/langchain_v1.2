# ch08/error_handling_modes.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool
from langchain_core.tools import ToolException

@tool
def risky_operation(data: str) -> str:
    """執行一個可能失敗的操作。

    Args:
        data: 輸入資料
    """

    if len(data) < 3:
        raise ToolException(f"輸入資料太短：'{data}'（至少需要 3 個字元）")

    return f"處理完成：{data.upper()}"

# === 方式一：布林值 True ===
# 直接將 ToolException 的訊息回傳給 LLM
risky_operation.handle_tool_error = True

# === 方式二：固定字串 ===
# 不論什麼錯誤，都回傳相同的訊息（適合對外隱藏內部錯誤細節）
risky_operation.handle_tool_error = "操作失敗，請檢查輸入資料後重試。"

# === 方式三：自訂函式 ===
# 根據錯誤類型，回傳不同的處理建議
def custom_error_handler(error: ToolException) -> str:
    error_msg = str(error)

    if "太短" in error_msg:
        return "輸入的資料太短了，請提供至少 3 個字元的資料。你可以請使用者補充更多資訊。"

    return f"工具執行遇到問題：{error_msg}。請嘗試其他方法。"

risky_operation.handle_tool_error = custom_error_handler
