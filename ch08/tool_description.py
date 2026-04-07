# ch08/tool_description.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool

# ❌ 糟糕的描述
@tool
def search_bad(query: str) -> str:
    """搜尋。"""
    return f"搜尋 {query} 的結果"

# ✅ 好的描述
@tool
def search_good(query: str) -> str:
    """在公司內部知識庫中搜尋技術文件和 FAQ。
    適用情境：當使用者詢問公司產品功能、技術規格、常見問題時使用。
    不適用：一般常識問題或與公司無關的查詢，這些請直接回答。

    Args:
        query: 搜尋關鍵字，建議使用具體的技術名詞或產品名稱。
               例如：'API rate limit' 或 '訂單匯出功能'
    """

    return f"在知識庫中搜尋「{query}」的結果"