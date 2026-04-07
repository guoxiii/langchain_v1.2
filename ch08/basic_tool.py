# ch08/basic_tool.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool

@tool
def get_word_count(text: str) -> str:
    """計算輸入文字的字數。

    Args:
        text: 要計算字數的文字內容
    """

    count = len(text)
    return f"這段文字共有 {count} 個字元"

# 查看工具的屬性
print(f"工具名稱：{get_word_count.name}")
print(f"工具描述：{get_word_count.description}")
print(f"參數定義：{get_word_count.args}")
