# vector_store.py

"""向量存儲模組 — Chroma"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.config import (
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)


class VectorStoreManager:
    """
    向量存儲管理器 — 負責 Chroma 的 CRUD 操作。
    把它想像成圖書館的電子目錄系統：
    書（chunk）進來時建立索引，
    讀者（使用者）來查詢時快速找到相關的書。
    """
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
        )

        self.vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )

    def add_documents(self, documents: list[Document]) -> list[str]:
        """
        將文件 chunks 加入向量存儲。

        Returns:
            新增的文件 ID 列表
        """
        ids = self.vectorstore.add_documents(documents)
        print(f"✅ 已將 {len(ids)} 個 chunks 加入向量存儲")
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: dict | None = None,
    ) -> list[Document]:
        """
        語義搜尋。

        Args:
            query: 使用者的查詢文字
            k: 回傳的結果數量
            filter_dict: metadata 過濾條件（用於權限控制）

        Returns:
            最相關的 Document 列表
        """
        kwargs = {"k": k}

        if filter_dict:
            kwargs["filter"] = filter_dict

        return self.vectorstore.similarity_search(query, **kwargs)

    def as_retriever(self, **kwargs):
        """取得 Retriever 物件（用於組合成 Ensemble Retriever）。"""
        return self.vectorstore.as_retriever(**kwargs)
