# ch10/faiss_with_score.py
"""FAISS 帶距離分數的搜尋"""

from dotenv import load_dotenv

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

documents = [
    Document(page_content="Python 是資料科學最受歡迎的程式語言。"),
    Document(page_content="JavaScript 是網頁開發的基石。"),
    Document(page_content="今天午餐吃了一碗牛肉麵。"),
]

vector_store = FAISS.from_documents(documents, embeddings)
query = "我想學資料分析"
results = vector_store.similarity_search_with_score(query=query, k=3)

print(f"🔍 搜尋：「{query}」\n")
print("⚠️ 注意：FAISS 回傳的是 L2 距離，數字越小越相似！\n")
for doc, score in results:
    print(f"  距離：{score:.4f}  📄 {doc.page_content}")
