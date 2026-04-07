# ch10/chroma_persistence.py
"""Chroma 持久化"""
from dotenv import load_dotenv

load_dotenv()

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

PERSIST_DIR = "./chroma_db"

# === 建立並持久化 ===
vector_store = Chroma.from_documents(
    documents=[
        Document(page_content="LangChain 是 LLM 應用開發框架。", metadata={"topic": "framework"}),
        Document(page_content="Chroma 是嵌入式向量資料庫。", metadata={"topic": "database"}),
        Document(page_content="RAG 是檢索增強生成技術。", metadata={"topic": "technique"}),
    ],
    embedding=embeddings,
    persist_directory=PERSIST_DIR,  # 指定持久化目錄
    collection_name="my_knowledge"
)

print(f"✅ 資料已持久化到 {PERSIST_DIR}")

# === 重新載入（模擬程式重新啟動）===
loaded_store = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
    collection_name="my_knowledge"
)

results = loaded_store.similarity_search("什麼是向量資料庫？", k=1)
print(f"🔍 從持久化資料搜尋：{results[0].page_content}")

# 查看 Collection 中的文件數量
print(f"📊 Collection 中共有 {loaded_store._collection.count()} 筆文件")
