# ch10/unified_interface.py
"""VectorStore 統一介面示範 — 一套程式碼，多種後端"""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.vectorstores import InMemoryVectorStore, VectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 準備共用的文件
documents = [
    Document(page_content="Python 是最受歡迎的 AI 程式語言。", metadata={"lang": "Python"}),
    Document(page_content="Rust 以記憶體安全著稱。", metadata={"lang": "Rust"}),
    Document(page_content="TypeScript 為 JavaScript 加入了型別系統。", metadata={"lang": "TypeScript"}),
]

def test_vector_store(store: VectorStore, name: str) -> None:
    """測試任何 VectorStore 的通用函式"""
    print(f"\n{'='*50}")
    print(f"🧪 測試 {name}")
    print(f"{'='*50}")

    # 1. 相似度搜尋
    results = store.similarity_search("AI 開發語言", k=2)
    print(f"\n  🔍 similarity_search 結果：")

    for doc in results:
        print(f"     - {doc.page_content}")

    # 2. 轉為 Retriever
    retriever = store.as_retriever(search_kwargs={"k": 1})
    docs = retriever.invoke("型別安全")

    print(f"\n  🔍 Retriever 結果：")

    for doc in docs:
        print(f"     - {doc.page_content}")

# 測試 InMemoryVectorStore
store1 = InMemoryVectorStore.from_documents(documents, embeddings)
test_vector_store(store1, "InMemoryVectorStore")

# 測試 FAISS（如果已安裝）
try:
    from langchain_community.vectorstores import FAISS
    store2 = FAISS.from_documents(documents, embeddings)
    test_vector_store(store2, "FAISS")
except ImportError:
    print("\n⚠️ FAISS 未安裝，跳過測試")

# 測試 Chroma（如果已安裝）
try:
    from langchain_chroma import Chroma
    store3 = Chroma.from_documents(documents, embeddings)
    test_vector_store(store3, "Chroma")
except ImportError:
    print("\n⚠️ Chroma 未安裝，跳過測試")
