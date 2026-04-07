# src/indexing/vector_index.py
"""向量索引管理 — 知識庫的搜尋引擎"""

from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from src.config import config

class VectorIndexManager:
    """
    Chroma 向量索引管理器

    核心功能：
    1. 建立與維護向量索引
    2. 增量添加文件
    3. 刪除文件（當文件被移除或更新時）
    4. 提供 Retriever 介面

    小比喻：如果向量資料庫是一座圖書館，
    這個管理器就是圖書館員——負責新書上架、
    舊書下架、幫你找到你想要的書。
    """

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.embedding_model,
        )
        self.vectorstore = Chroma(
            collection_name=config.chroma_collection,
            embedding_function=self.embeddings,
            persist_directory=config.chroma_persist_dir,
        )

    def add_documents(
        self, documents: list[Document], doc_id: str
    ) -> list[str]:
        """
        將文件的 chunks 加入向量索引

        Parameters
        ----------

        documents : list[Document]
            切割後的 Document 列表

        doc_id : str
            來源文件 ID（用於後續刪除/更新）

        Returns
        -------

        list[str]
            Chroma 分配的向量 ID 列表
        """

        # 確保每個 chunk 都帶有 doc_id
        for doc in documents:
            doc.metadata["doc_id"] = doc_id

        # 使用 doc_id + chunk_index 作為穩定 ID
        ids = [
            f"{doc_id}_chunk_{doc.metadata.get('chunk_index', i)}"
            for i, doc in enumerate(documents)
        ]

        vector_ids = self.vectorstore.add_documents(
            documents=documents,
            ids=ids,
        )

        print(f"📥 已索引 {len(vector_ids)} 個 chunks（doc_id: {doc_id}）")
        return vector_ids

    def delete_document(self, doc_id: str) -> None:
        """刪除指定文件的所有向量"""
        # 使用 Chroma 的 where 篩選器找出所有相關向量
        results = self.vectorstore.get(
            where={"doc_id": doc_id}
        )

        if results and results["ids"]:
            self.vectorstore.delete(ids=results["ids"])
            print(f"🗑️ 已刪除 {len(results['ids'])} 個 chunks（doc_id: {doc_id}）")
        else:
            print(f"⚠️ 找不到 doc_id: {doc_id} 的向量")

    def update_document(
        self, documents: list[Document], doc_id: str
    ) -> list[str]:
        """更新文件：先刪除舊的，再加入新的"""
        self.delete_document(doc_id)
        return self.add_documents(documents, doc_id)

    def get_retriever(self, **kwargs):
        """
        取得 Retriever 實例
        預設使用 MMR（Maximal Marginal Relevance）搜尋，
        這比純相似度搜尋多了一層「多樣性」考量——
        避免回傳五個幾乎一模一樣的結果。
        """
        return self.vectorstore.as_retriever(
            search_type=kwargs.get("search_type", config.retriever_search_type),
            search_kwargs={
                "k": kwargs.get("k", config.retriever_k),
            },
        )

    def similarity_search(
        self, query: str, k: int = 5, filter_dict: dict | None = None
    ) -> list[Document]:
        """直接進行相似度搜尋（帶篩選條件）"""
        kwargs = {"k": k}

        if filter_dict:
            kwargs["filter"] = filter_dict

        return self.vectorstore.similarity_search(query, **kwargs)
