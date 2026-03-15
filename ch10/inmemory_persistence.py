# ch10/inmemory_persistence.py
"""InMemoryVectorStore 的持久化"""
from dotenv import load_dotenv

load_dotenv()

import json
from pathlib import Path
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# === 儲存 ===
vector_store = InMemoryVectorStore(embedding=embeddings)

vector_store.add_documents([
    Document(id="1", page_content="LangChain 是一個強大的 LLM 應用開發框架。"),
    Document(id="2", page_content="RAG 可以讓 LLM 存取外部知識。"),
])

# 匯出到 JSON 檔案
dump_path = Path("my_vector_store.json")
vector_store.dump(str(dump_path))

print(f"✅ Vector Store 已儲存到 {dump_path}")

# === 載入 ===
loaded_store = InMemoryVectorStore.load(
    str(dump_path),
    embedding=embeddings
)

results = loaded_store.similarity_search("什麼是 RAG？", k=1)
print(f"🔍 從載入的 Store 搜尋：{results[0].page_content}")
