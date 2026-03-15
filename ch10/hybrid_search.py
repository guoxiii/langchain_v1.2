# ch10/hybrid_search.py
"""Hybrid Search — 結合向量搜尋與關鍵字搜尋"""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 準備文件
documents = [
    Document(page_content="create_agent 是 LangChain v1 建立 Agent 的核心函式。"),
    Document(page_content="Agent 能夠自主推理、使用工具來解決複雜問題。"),
    Document(page_content="create_agent 回傳一個 CompiledStateGraph 物件。"),
    Document(page_content="Middleware 系統讓你可以在 Agent 的各個階段插入邏輯。"),
    Document(page_content="LLM 是大型語言模型的縮寫，是 AI 應用的核心。"),
    Document(page_content="LangChain 的 Tool 定義支援 @tool 裝飾器和 BaseTool 類別。"),
]

# 建立向量搜尋 Retriever
vector_store = InMemoryVectorStore.from_documents(documents, embeddings)
vector_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 建立 BM25 關鍵字搜尋 Retriever
bm25_retriever = BM25Retriever.from_documents(documents, k=3)

# 建立 Ensemble Retriever（混合搜尋）
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5]  # 向量搜尋和關鍵字搜尋各佔 50%
)

query = "create_agent"

# 比較三種搜尋的結果
print(f"🔍 查詢：「{query}」\n")
print("📌 純向量搜尋：")

for doc in vector_retriever.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")

print("\n📌 純 BM25 關鍵字搜尋：")

for doc in bm25_retriever.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")

print("\n📌 Hybrid Search（混合搜尋）：")

for doc in ensemble_retriever.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")
