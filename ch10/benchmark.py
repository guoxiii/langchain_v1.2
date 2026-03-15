# ch10/benchmark.py
"""Vector Store 效能比較實驗"""
from dotenv import load_dotenv

load_dotenv()

import time
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ✅ 修復：補上 InMemoryVectorStore 缺少的 relevance score function
class PatchedInMemoryVectorStore(InMemoryVectorStore):
    def _select_relevance_score_fn(self):
        # InMemoryVectorStore 使用餘弦相似度，值域已是 [0, 1]，直接回傳即可
        return lambda score: score

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# ============================================================
# 準備測試資料 — 模擬一個技術文件知識庫
# ============================================================

documents = [
    # Python 相關
    Document(page_content="Python 的 list comprehension 語法讓你一行就能建立列表。", metadata={"topic": "Python", "level": "beginner"}),
    Document(page_content="Python 的 GIL（全域直譯器鎖）限制了多執行緒的平行效能。", metadata={"topic": "Python", "level": "advanced"}),
    Document(page_content="Python 的 asyncio 模組提供了非同步 I/O 的支援。", metadata={"topic": "Python", "level": "intermediate"}),
    Document(page_content="Python 的 dataclass 裝飾器可以簡化資料類別的定義。", metadata={"topic": "Python", "level": "intermediate"}),
    Document(page_content="Python 的 type hints 在 3.10 之後支援了更簡潔的語法。", metadata={"topic": "Python", "level": "intermediate"}),
    # LangChain 相關
    Document(page_content="LangChain 的 create_agent 函式取代了舊版的 create_react_agent。", metadata={"topic": "LangChain", "level": "intermediate"}),
    Document(page_content="LangChain 的 Middleware 系統提供了六大 Hook 用於控制 Agent 行為。", metadata={"topic": "LangChain", "level": "advanced"}),
    Document(page_content="LangChain 的 init_chat_model 支援一行程式碼切換模型供應商。", metadata={"topic": "LangChain", "level": "beginner"}),
    Document(page_content="LangChain v1 不再支援 LCEL 管道語法，改用 create_agent。", metadata={"topic": "LangChain", "level": "intermediate"}),
    # RAG 相關
    Document(page_content="RAG 的核心是讓 LLM 能夠存取外部知識，避免幻覺問題。", metadata={"topic": "RAG", "level": "beginner"}),
    Document(page_content="Chunk Size 的選擇會直接影響 RAG 的檢索品質和回答品質。", metadata={"topic": "RAG", "level": "intermediate"}),
    Document(page_content="GraphRAG 結合了知識圖譜和向量搜尋，適合處理複雜關聯查詢。", metadata={"topic": "RAG", "level": "advanced"}),
    # 其他
    Document(page_content="Docker 容器化技術讓應用部署變得更加便捷和一致。", metadata={"topic": "DevOps", "level": "beginner"}),
    Document(page_content="PostgreSQL 是最強大的開源關聯式資料庫。", metadata={"topic": "Database", "level": "beginner"}),
    Document(page_content="Redis 是高效能的記憶體資料庫，常用於快取和訊息佇列。", metadata={"topic": "Database", "level": "intermediate"}),
]

# 測試查詢
queries = [
    "Python 的非同步程式設計怎麼做？",
    "LangChain 最新版本有什麼改變？",
    "如何提升 RAG 的效果？",
    "資料庫有哪些選擇？",
]

def benchmark_store(store_name: str, vector_store, queries: list[str]) -> None:
    """對指定的 Vector Store 進行效能測試"""
    print(f"\n{'='*60}")
    print(f"🏋️ {store_name}")
    print(f"{'='*60}")

    total_time = 0

    for query in queries:
        start = time.perf_counter()
        results = vector_store.similarity_search(query, k=3)
        elapsed = time.perf_counter() - start
        total_time += elapsed

        print(f"\n  🔍 「{query}」 ({elapsed*1000:.1f} ms)")

        for i, doc in enumerate(results, 1):
            print(f"     {i}. [{doc.metadata.get('topic', '?')}] {doc.page_content[:40]}...")

    avg_time = (total_time / len(queries)) * 1000
    print(f"\n  ⏱️ 平均搜尋時間：{avg_time:.1f} ms")

# ============================================================
# 測試各個 Vector Store
# ============================================================

# 1. InMemoryVectorStore
print("\n⏳ 建立 InMemoryVectorStore...")

start = time.perf_counter()
# store_memory = InMemoryVectorStore.from_documents(documents, embeddings)
# ✅ 改用修補後的子類別
store_memory = PatchedInMemoryVectorStore.from_documents(documents, embeddings)
build_time = time.perf_counter() - start

print(f"   建立耗時：{build_time:.2f} 秒")

benchmark_store("InMemoryVectorStore", store_memory, queries)

# 2. FAISS
try:
    from langchain_community.vectorstores import FAISS

    print("\n\n⏳ 建立 FAISS...")

    start = time.perf_counter()
    store_faiss = FAISS.from_documents(documents, embeddings)
    build_time = time.perf_counter() - start

    print(f"   建立耗時：{build_time:.2f} 秒")

    benchmark_store("FAISS", store_faiss, queries)
except ImportError:
    print("\n⚠️ FAISS 未安裝，跳過（安裝方式：uv add langchain-community faiss-cpu）")

# 3. Chroma
try:
    from langchain_chroma import Chroma

    print("\n\n⏳ 建立 Chroma...")

    start = time.perf_counter()
    store_chroma = Chroma.from_documents(documents, embeddings)
    build_time = time.perf_counter() - start

    print(f"   建立耗時：{build_time:.2f} 秒")

    benchmark_store("Chroma", store_chroma, queries)
except ImportError:
    print("\n⚠️ Chroma 未安裝，跳過（安裝方式：uv add langchain-chroma chromadb）")

# ============================================================
# 測試 Retriever 搜尋策略
# ============================================================

print(f"\n\n{'='*60}")
print("🎯 Retriever 搜尋策略比較")
print(f"{'='*60}")

query = "LangChain 的新功能"

# similarity
retriever_sim = store_memory.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

print(f"\n📌 similarity 策略（查詢：「{query}」）：")
for doc in retriever_sim.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")

# mmr
retriever_mmr = store_memory.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5}
)

print(f"\n📌 mmr 策略（查詢：「{query}」）：")

for doc in retriever_mmr.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")

# similarity_score_threshold
retriever_threshold = store_memory.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.3}
)

print(f"\n📌 similarity_score_threshold 策略（查詢：「{query}」）：")

results = retriever_threshold.invoke(query)

if results:
    for doc in results:
        print(f"  📄 {doc.page_content[:50]}...")
else:
    print("  ⚠️ 沒有達到閾值的結果")

print("\n✅ 所有測試完成！")
