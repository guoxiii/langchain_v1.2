# ch10/inmemory_with_score.py
"""InMemoryVectorStore 帶分數的相似度搜尋"""

from dotenv import load_dotenv

load_dotenv()

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

vector_store = InMemoryVectorStore(embedding=embeddings)

documents = [
    Document(id="1", page_content="Python 是一種簡單易學的程式語言，適合初學者入門。"),
    Document(id="2", page_content="JavaScript 是網頁前端開發的核心語言。"),
    Document(id="3", page_content="今天天氣真好，適合出去走走。"),
    Document(id="4", page_content="Rust 語言以記憶體安全和高效能著稱。"),
]

vector_store.add_documents(documents=documents)
query = "我想學程式設計"
results = vector_store.similarity_search_with_score(query=query, k=4)

print(f"🔍 搜尋：「{query}」\n")

for doc, score in results:
    print(f"  分數：{score:.4f}")
    print(f"  內容：{doc.page_content}")
    print()
