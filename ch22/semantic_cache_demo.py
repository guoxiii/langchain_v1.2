"""
檔案：semantic_cache_demo.py
語義快取實作範例
"""

import hashlib
import json
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

class SemanticCache:
    """
    語義快取：用 Embedding 比對查詢相似度，
    相似度超過閾值就直接回傳快取結果。
    """
    def __init__(
        self,
        embeddings_model: str = "google_genai:gemini-embedding-001",
        similarity_threshold: float = 0.92,
        ttl_seconds: int = 3600,
    ):
        self.embeddings = init_embeddings(embeddings_model)
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self.cache_data: dict[str, dict] = {}  # doc_id -> {response, timestamp}

    def _generate_id(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[str]:
        """嘗試從快取中取得語義相似的回應"""
        results = self.vector_store.similarity_search_with_score(
            query, k=1
        )

        if not results:
            return None

        doc, score = results[0]
        print(f"  🔍 DEBUG: score={score:.4f}, threshold={self.similarity_threshold}")

        # 檢查相似度是否超過閾值
        if score < self.similarity_threshold:
            return None

        # 檢查是否已過期
        cache_entry = self.cache_data.get(doc.metadata["cache_id"])

        if not cache_entry:
            return None

        if time.time() - cache_entry["timestamp"] > self.ttl_seconds:
            # 已過期，移除快取
            del self.cache_data[doc.metadata["cache_id"]]
            return None

        print(f"  🎯 快取命中！相似度: {score:.4f}")
        return cache_entry["response"]

    def set(self, query: str, response: str) -> None:
        """將查詢和回應存入快取"""
        cache_id = self._generate_id(query)
        self.vector_store.add_documents([
            Document(
                page_content=query,
                metadata={"cache_id": cache_id},
            )
        ])

        self.cache_data[cache_id] = {
            "response": response,
            "timestamp": time.time(),
        }

# ---- 使用範例 ----
cache = SemanticCache(similarity_threshold=0.80)
model = init_chat_model("google_genai:gemini-2.5-flash")

def ask_with_cache(question: str) -> str:
    """帶有語義快取的問答函式"""
    # 1. 先查快取
    cached = cache.get(question)

    if cached:
        return cached

    # 2. 快取未命中，呼叫模型
    print("  📡 呼叫 LLM API...")

    response = model.invoke(question)
    answer = response.content

    # 3. 存入快取
    cache.set(question, answer)
    return answer

# 測試語義快取
print("第一次查詢：")
print(ask_with_cache("台北今天的天氣如何？"))
print("\n語義相似的查詢：")
print(ask_with_cache("台北天氣怎樣"))  # 應該會命中快取
