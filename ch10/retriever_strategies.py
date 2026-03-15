# ch10/retriever_strategies.py
"""Retriever 搜尋策略比較：similarity vs mmr"""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 故意準備一些內容相似但角度不同的文件
documents = [
    Document(page_content="Python 是一種直譯式的高階程式語言，以簡潔的語法著稱。"),
    Document(page_content="Python 語言的設計哲學是「優雅」、「明確」、「簡單」。"),
    Document(page_content="Python 廣泛應用於資料科學、機器學習和人工智慧領域。"),
    Document(page_content="Python 有豐富的第三方套件生態系統，pip 是主要的套件管理工具。"),
    Document(page_content="JavaScript 是瀏覽器端最重要的程式語言。"),
    Document(page_content="Rust 語言在系統程式設計領域越來越受歡迎。"),
    Document(page_content="Go 語言以簡潔和高效的並發處理能力聞名。"),
    Document(page_content="Java 是企業級應用開發最主流的語言。"),
]

vector_store = InMemoryVectorStore.from_documents(documents, embeddings)
query = "我想了解 Python"

# 策略一：similarity — 最相似的 4 筆
print("📌 策略：similarity")
print("-" * 50)

retriever_sim = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

for doc in retriever_sim.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")

# 策略二：mmr — 兼顧相關性和多樣性
print("\n📌 策略：mmr (lambda_mult=0.5)")
print("-" * 50)

retriever_mmr = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 8, "lambda_mult": 0.5}
)

for doc in retriever_mmr.invoke(query):
    print(f"  📄 {doc.page_content[:50]}...")
