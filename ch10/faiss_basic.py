# ch10/faiss_basic.py
"""FAISS 基本用法 — from_documents 快速建立"""
from dotenv import load_dotenv

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 準備文件
documents = [
    Document(
        page_content="LangChain 是一個用於建構 LLM 應用的開源框架，提供了豐富的工具和抽象層。",
        metadata={"source": "langchain_intro.md", "category": "framework"}
    ),
    Document(
        page_content="RAG（檢索增強生成）是一種結合檢索系統與生成模型的技術，能讓 AI 存取最新的外部知識。",
        metadata={"source": "rag_guide.md", "category": "technique"}
    ),
    Document(
        page_content="向量資料庫專門用於儲存和搜尋高維向量，是 RAG 系統的核心元件之一。",
        metadata={"source": "vector_db.md", "category": "infrastructure"}
    ),
    Document(
        page_content="Prompt Engineering 是設計與優化 LLM 輸入提示的技術，直接影響模型輸出品質。",
        metadata={"source": "prompt_eng.md", "category": "technique"}
    ),
    Document(
        page_content="Agent 是能夠自主決策、使用工具來完成任務的 AI 系統，是 LangChain 的核心功能之一。",
        metadata={"source": "agent_intro.md", "category": "framework"}
    ),
]

# 用 from_documents 一步建立 FAISS Vector Store
vector_store = FAISS.from_documents(
    documents=documents,
    embedding=embeddings
)

print(f"✅ FAISS Vector Store 已建立，共 {vector_store.index.ntotal} 筆向量")

# 搜尋
query = "如何讓 AI 使用外部資料？"
results = vector_store.similarity_search(query=query, k=3)

print(f"\n🔍 搜尋：「{query}」\n")

for i, doc in enumerate(results, 1):
    print(f"  📄 結果 {i}: {doc.page_content[:50]}...")
    print(f"     來源: {doc.metadata['source']}\n")
