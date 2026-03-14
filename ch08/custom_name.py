# ch08/custom_name.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool

@tool("word_counter", description="計算中英文混合文字的字元數量，包含空格與標點符號。")
def my_internal_function_name(text: str) -> str:
    """這個 docstring 不會被使用，因為我們已經在裝飾器中指定了 description。"""
    count = len(text)
    return f"字元數量：{count}"

print(f"工具名稱：{my_internal_function_name.name}")       # word_counter
print(f"工具描述：{my_internal_function_name.description}")  # 計算中英文混合...
