# hybrid_retriever.py

"""混合檢索器 — 結合 Vector + Graph + BM25"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from src.vector_store import VectorStoreManager
from src.graph_retriever import GraphRetrieverModule
from src.config import VECTOR_SEARCH_K, GRAPH_SEARCH_K

class HybridRetriever:
    """
    混合檢索器 — 三劍合璧。    

    結合三種檢索方式的優勢：
    - Vector Search：捕捉語義相似性
    - Graph Traversal：捕捉實體間的關係
    - BM25 Keyword Search：捕捉精確的關鍵字匹配    

    最終通過 Ensemble Retriever 進行結果融合。
    """

    def __init__(self, all_chunks: list[Document] | None = None):
        """
        Args:
            all_chunks: 所有文件 chunks（BM25 需要全量文件建索引）
        """
        self.vector_store = VectorStoreManager()
        self.graph_retriever = GraphRetrieverModule()

        # BM25 需要全量文件（如果有提供的話）
        self.bm25_retriever = None

        if all_chunks:
            self.bm25_retriever = BM25Retriever.from_documents(
                all_chunks
            )

            self.bm25_retriever.k = VECTOR_SEARCH_K

    def retrieve(
        self,
        query: str,
        user_access_level: str = "public",
        user_department: str | None = None,
    ) -> list[Document]:
        """
        執行混合檢索。

        Args:
            query: 使用者的查詢
            user_access_level: 使用者的存取級別
            user_department: 使用者所屬部門

        Returns:
            融合後的相關 Document 列表
        """

        all_results: list[Document] = []

        # ── 1. Vector Search ──
        print("🔍 執行 Vector Search...")

        access_filter = self._build_access_filter(
            user_access_level, user_department
        )

        vector_results = self.vector_store.similarity_search(
            query,
            k=VECTOR_SEARCH_K,
            filter_dict=access_filter,
        )

        for doc in vector_results:
            doc.metadata["retrieval_method"] = "vector_search"

        all_results.extend(vector_results)
        print(f"   找到 {len(vector_results)} 個結果")

        # ── 2. Graph Traversal ──
        print("🔍 執行 Graph Traversal...")
        graph_results = self.graph_retriever.search(query)

        for doc in graph_results:
            doc.metadata["retrieval_method"] = "graph_traversal"

        all_results.extend(graph_results)
        print(f"   找到 {len(graph_results)} 個結果")

        # ── 3. BM25 Keyword Search（如果有的話）──
        if self.bm25_retriever:
            print("🔍 執行 BM25 Keyword Search...")
            bm25_results = self.bm25_retriever.invoke(query)

            # 套用權限過濾
            bm25_results = self._filter_by_access(
                bm25_results, user_access_level, user_department
            )

            for doc in bm25_results:
                doc.metadata["retrieval_method"] = "bm25_keyword"

            all_results.extend(bm25_results)
            print(f"   找到 {len(bm25_results)} 個結果")

        # ── 去重 ──
        deduplicated = self._deduplicate(all_results)
        print(f"\n📊 混合檢索完成：共 {len(deduplicated)} 個不重複結果")
        return deduplicated

    def _build_access_filter(
        self,
        access_level: str,
        department: str | None,
    ) -> dict | None:
        """
        建立 Chroma 的 metadata 過濾條件。

        權限邏輯：
        - "public" 級別：只能看到 public 文件
        - "internal" 級別：可看 public + internal
        - "confidential" 級別：可看所有文件
        """
        access_hierarchy = {
            "public": ["public"],
            "internal": ["public", "internal"],
            "confidential": ["public", "internal", "confidential"],
        }

        allowed_levels = access_hierarchy.get(access_level, ["public"])
        filter_dict: dict = {"access_level": {"$in": allowed_levels}}

        return filter_dict

    def _filter_by_access(
        self,
        documents: list[Document],
        access_level: str,
        department: str | None,
    ) -> list[Document]:
        """對 BM25 結果手動套用權限過濾。"""
        access_hierarchy = {
            "public": ["public"],
            "internal": ["public", "internal"],
            "confidential": ["public", "internal", "confidential"],
        }

        allowed = access_hierarchy.get(access_level, ["public"])

        return [
            doc
            for doc in documents
            if doc.metadata.get("access_level", "public") in allowed
        ]

    def _deduplicate(
        self, documents: list[Document]
    ) -> list[Document]:
        """根據內容 hash 去除重複結果。"""
        seen: set[str] = set()
        unique: list[Document] = []

        for doc in documents:
            content_hash = doc.metadata.get(
                "doc_hash",
                str(hash(doc.page_content[:200])),
            )

            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(doc)

        return unique
