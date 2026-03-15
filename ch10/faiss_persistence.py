# ch10/faiss_persistence.py
"""FAISS 索引的儲存與載入"""
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

index_path = Path("faiss_index")

# === 第一次：建立並儲存 ===
if not index_path.exists():
    documents = [
        Document(page_content="LangChain 讓建構 AI 應用變得簡單。"),
        Document(page_content="FAISS 是高效能的向量搜尋函式庫。"),
        Document(page_content="RAG 結合了檢索與生成的優點。"),
    ]

    vector_store = FAISS.from_documents(documents, embeddings)

    # 儲存到本地
    vector_store.save_local(str(index_path))

    print(f"✅ FAISS 索引已儲存到 {index_path}/")
else:
    print(f"📂 從 {index_path}/ 載入既有索引...")

# === 載入 ===
loaded_store = FAISS.load_local(
    str(index_path),
    embeddings=embeddings,
    allow_dangerous_deserialization=True  # FAISS 使用 pickle，需要明確同意
)

results = loaded_store.similarity_search("向量搜尋", k=1)

print(f"🔍 搜尋結果：{results[0].page_content}")
