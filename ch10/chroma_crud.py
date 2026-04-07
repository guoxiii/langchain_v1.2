# ch10/chroma_crud.py
"""Chroma 文件的新增與刪除"""
from dotenv import load_dotenv

load_dotenv()

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 建立 Chroma
vector_store = Chroma(
    embedding_function=embeddings,
    collection_name="demo"
)

# 新增文件（add_documents 會回傳 ID 列表）
ids = vector_store.add_documents([
    Document(page_content="第一筆文件"),
    Document(page_content="第二筆文件"),
    Document(page_content="第三筆文件"),
])

print(f"✅ 新增了 {len(ids)} 筆文件")
print(f"   IDs: {ids}")

# 用文字直接新增（不需要包成 Document）
text_ids = vector_store.add_texts(
    texts=["第四筆文件", "第五筆文件"],
    metadatas=[{"source": "manual"}, {"source": "manual"}]
)

print(f"✅ 又新增了 {len(text_ids)} 筆文件")

# 查看總數
print(f"📊 目前共有 {vector_store._collection.count()} 筆文件")

# 刪除特定文件
vector_store.delete(ids=[ids[2]])  # 刪除第三筆
print(f"🗑️ 刪除後共有 {vector_store._collection.count()} 筆文件")
