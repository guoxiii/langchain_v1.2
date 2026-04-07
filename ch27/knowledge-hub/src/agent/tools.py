# src/agent/tools.py
"""Agent 工具定義 — Agent 的瑞士刀"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.tools import tool
from src.indexing.vector_index import VectorIndexManager
from src.indexing.graph_index import GraphIndexManager

# 初始化索引管理器（模組級別，避免重複建立）
_vector_index = VectorIndexManager()
_graph_index = GraphIndexManager()

@tool
def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """
    在企業知識庫中搜尋與查詢最相關的文件片段。
    使用這個工具來回答關於公司文件、技術文檔、
    產品規格、流程規範等問題。

    Args:
        query: 搜尋查詢，使用自然語言描述你要找的資訊
        top_k: 回傳的結果數量，預設 5

    Returns:
        找到的相關文件片段，包含來源資訊
    """

    results = _vector_index.similarity_search(query, k=top_k)

    if not results:
        return "在知識庫中沒有找到相關文件。請嘗試用不同的關鍵字搜尋。"

    formatted = []

    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("title", "未知")
        doc_id = doc.metadata.get("doc_id", "N/A")
        chunk_idx = doc.metadata.get("chunk_index", "N/A")
        formatted.append(
            f"【結果 {i}】\n"
            f"來源：{source}（doc_id: {doc_id}, chunk: {chunk_idx}）\n"
            f"內容：{doc.page_content}\n"
        )

    return "\n---\n".join(formatted)

@tool
def query_knowledge_graph(concept: str, depth: int = 2) -> str:
    """
    查詢知識圖譜中與某個概念相關的實體和關係。
    當使用者問到「XX 和 YY 是什麼關係」、「跟 XX 相關的有哪些」
    這類關聯性問題時，使用這個工具。

    Args:
        concept: 要查詢的概念或實體名稱
        depth: 關係搜尋深度，1=直接關聯，2=二度關聯

    Returns:
        相關實體及其關係的描述
    """

    results = _graph_index.query_related_concepts(concept, depth=depth)

    if not results:
        return f"在知識圖譜中沒有找到與「{concept}」相關的資訊。"

    return f"找到 {len(results)} 筆與「{concept}」相關的資料：\n{str(results[:10])}"

@tool
def list_available_documents() -> str:
    """
    列出知識庫中所有可用的文件。
    當使用者問「知識庫裡有哪些文件」、「有什麼資料可以查」時，
    使用這個工具。

    Returns:
        所有已索引文件的列表，包含標題和摘要
    """

    import json
    from pathlib import Path

    metadata_path = Path("./data/metadata.json")

    if not metadata_path.exists():
        return "目前知識庫中沒有文件。"

    with open(metadata_path, "r", encoding="utf-8") as f:
        store = json.load(f)

    if not store:
        return "目前知識庫中沒有文件。"

    docs_info = []

    for doc_id, meta in store.items():
        title = meta.get("title", "未命名")
        summary = meta.get("summary", "無摘要")
        status = meta.get("status", "unknown")
        tags = ", ".join(meta.get("tags", []))

        docs_info.append(
            f"- 📄 {title} (ID: {doc_id})\n"
            f"  狀態：{status} | 標籤：{tags or '無'}\n"
            f"  摘要：{summary[:100]}..."
        )

    return f"知識庫共有 {len(store)} 份文件：\n\n" + "\n\n".join(docs_info)
