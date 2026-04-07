# calculator_server.py

"""一個簡單的計算器 MCP Server"""
from mcp.server.fastmcp import FastMCP

# 建立 MCP Server 實例
# "Calculator" 是這個 Server 的名稱，會顯示在 Client 端
mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """將兩個數字相加。

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數相加的結果
    """
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """將兩個數字相乘。

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數相乘的結果
    """
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> str:
    """將第一個數字除以第二個數字。

    Args:
        a: 被除數
        b: 除數

    Returns:
        除法結果，如果除數為零則回傳錯誤訊息
    """

    if b == 0:
        return "錯誤：除數不能為零！"

    return str(a / b)

# 用 stdio 傳輸方式啟動 Server

if __name__ == "__main__":
    mcp.run(transport="stdio")
