# ch10/chroma_filter.py
"""Chroma 進階 Metadata 過濾"""
from dotenv import load_dotenv

load_dotenv()

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

documents = [
    Document(page_content="Flask 是輕量級的 Python Web 框架。", metadata={"language": "Python", "stars": 65000, "year": 2010}),
    Document(page_content="Express.js 是 Node.js 的極簡 Web 框架。", metadata={"language": "JavaScript", "stars": 63000, "year": 2010}),
    Document(page_content="FastAPI 是高效能的現代 Python 框架。", metadata={"language": "Python", "stars": 78000, "year": 2019}),
    Document(page_content="Next.js 是 React 的全端框架。", metadata={"language": "JavaScript", "stars": 125000, "year": 2016}),
    Document(page_content="Gin 是 Go 語言最受歡迎的 Web 框架。", metadata={"language": "Go", "stars": 79000, "year": 2014}),
    Document(page_content="Axum 是 Rust 生態系中新興的 Web 框架。", metadata={"language": "Rust", "stars": 20000, "year": 2021}),
]

vector_store = Chroma.from_documents(documents, embeddings)
query = "好用的 Web 框架"

# 過濾 1：只搜尋 Python 語言的
print("📌 過濾 1：只搜尋 Python 語言")

results = vector_store.similarity_search(
    query=query, k=3,
    filter={"language": "Python"}
)

for doc in results:
    print(f"  📄 {doc.page_content}")

# 過濾 2：搜尋 Star 數大於 70000 的
print("\n📌 過濾 2：Star 數 > 70000")

results = vector_store.similarity_search(
    query=query, k=3,
    filter={"stars": {"$gt": 70000}}
)

for doc in results:
    print(f"  📄 {doc.page_content} (⭐ {doc.metadata['stars']})")

# 過濾 3：搜尋 2015 年以後的 Python 或 Rust 框架
print("\n📌 過濾 3：2015 年後的 Python 或 Rust 框架")

results = vector_store.similarity_search(
    query=query, k=3,
    filter={
        "$and": [
            {"year": {"$gte": 2015}},
            {"language": {"$in": ["Python", "Rust"]}}
        ]
    }
)

for doc in results:
    print(f"  📄 {doc.page_content} ({doc.metadata['language']}, {doc.metadata['year']})")
