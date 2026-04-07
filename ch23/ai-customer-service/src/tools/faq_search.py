# src/tools/faq_search.py
"""
FAQ 知識庫搜尋工具。
Agent 會使用這個工具從知識庫中查找客戶問題的答案。
"""

from langchain_core.tools import tool
from src.rag.build_knowledge_base import load_knowledge_base

@tool
def search_faq(query: str) -> str:
    """搜尋 FAQ 知識庫，根據客戶的問題查找最相關的答案。
    當客戶詢問關於退貨、退款、運費、帳號、商品保固、折扣碼等
    常見問題時，使用此工具搜尋知識庫中的標準答案。

    Args:
        query: 客戶的問題或關鍵字

    Returns:
        最相關的 FAQ 答案，包含來源分類資訊
    """

    vectorstore = load_knowledge_base()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )

    docs = retriever.invoke(query)

    if not docs:
        return "抱歉，知識庫中找不到與此問題相關的資訊。建議轉接人工客服處理。"

    # 組合搜尋結果
    results = []

    for i, doc in enumerate(docs, 1):
        category = doc.metadata.get("category", "未分類")
        results.append(
            f"【搜尋結果 {i}】（分類：{category}）\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(results)
