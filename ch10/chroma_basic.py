# ch10/chroma_basic.py
"""Chroma 基本用法"""
from dotenv import load_dotenv

load_dotenv()

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 準備文件
documents = [
    Document(
        page_content="FastAPI 是一個高效能的 Python Web 框架，支援自動產生 API 文件。",
        metadata={"language": "Python", "type": "web_framework", "year": 2019}
    ),
    Document(
        page_content="Django 是 Python 最受歡迎的全端 Web 框架，內建 ORM 和管理後台。",
        metadata={"language": "Python", "type": "web_framework", "year": 2005}
    ),
    Document(
        page_content="React 是由 Meta 開發的 JavaScript 前端框架，使用虛擬 DOM 提升效能。",
        metadata={"language": "JavaScript", "type": "frontend_framework", "year": 2013}
    ),
    Document(
        page_content="Rust 的 Actix-web 是效能極高的 Web 框架，適合高併發場景。",
        metadata={"language": "Rust", "type": "web_framework", "year": 2017}
    ),
    Document(
        page_content="Vue.js 是一個漸進式的 JavaScript 前端框架，學習曲線平緩。",
        metadata={"language": "JavaScript", "type": "frontend_framework", "year": 2014}
    ),
]

# 建立 Chroma（純記憶體模式）
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    collection_name="frameworks"  # 指定 Collection 名稱
)

# 基本搜尋
query = "適合建立 REST API 的工具"
results = vector_store.similarity_search(query=query, k=3)
print(f"🔍 搜尋：「{query}」\n")

for i, doc in enumerate(results, 1):
    print(f"  📄 結果 {i}: {doc.page_content[:50]}...")
    print(f"     語言: {doc.metadata['language']}  年份: {doc.metadata['year']}\n")
