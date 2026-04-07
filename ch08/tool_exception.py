# ch08/tool_exception.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool
from langchain_core.tools import ToolException

@tool
def divide(a: float, b: float) -> str:
    """將兩個數字相除。

    Args:
        a: 被除數
        b: 除數（不可為 0）
    """

    if b == 0:
        raise ToolException(
            "除數不能為 0！請提供一個非零的除數。"
        )

    result = a / b
    return f"{a} ÷ {b} = {result:.4f}"

# 設定錯誤處理方式
divide.handle_tool_error = True  # 將 ToolException 的訊息回傳給 LLM

# 測試正常情況
print(divide.invoke({"a": 10, "b": 3}))

# 輸出：10 ÷ 3 = 3.3333
# 測試錯誤情況
print(divide.invoke({"a": 10, "b": 0}))

# 輸出：除數不能為 0！請提供一個非零的除數。
