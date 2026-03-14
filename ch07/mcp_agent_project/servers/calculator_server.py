# servers/calculator_server.py

"""計算器 MCP Server — 提供基本的數學運算"""
import math
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """將兩個數字相加。

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數之和
    """
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """將第一個數字減去第二個數字。

    Args:
        a: 被減數
        b: 減數

    Returns:
        兩數之差
    """
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """將兩個數字相乘。

    Args:
        a: 第一個數字
        b: 第二個數字

    Returns:
        兩數之積
    """
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> str:
    """將第一個數字除以第二個數字。

    Args:
        a: 被除數
        b: 除數（不可為零）

    Returns:
        除法結果。如果除數為零，回傳錯誤訊息
    """
    if b == 0:
        return "錯誤：除數不能為零！"

    return str(a / b)

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """計算次方。

    Args:
        base: 底數
        exponent: 指數

    Returns:
        base 的 exponent 次方
    """
    return math.pow(base, exponent)

@mcp.tool()
def sqrt(number: float) -> str:
    """計算平方根。

    Args:
        number: 要計算平方根的數字（必須非負）

    Returns:
        平方根結果。如果輸入為負數，回傳錯誤訊息
    """
    if number < 0:
        return "錯誤：無法計算負數的平方根！"

    return str(math.sqrt(number))

if __name__ == "__main__":
    mcp.run(transport="stdio")
