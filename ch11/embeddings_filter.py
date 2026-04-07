# 檔案名稱：embeddings_filter.py
# 功能：使用 EmbeddingsFilter 過濾低相關性文件
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter

# === 1. 建立基礎 Retriever ===
documents = [
    Document(page_content="Python 的 decorator 是一個高階函式，使用 @decorator_name 語法套用。"),
    Document(page_content="Python 支援物件導向程式設計，使用 class 關鍵字定義類別。"),
    Document(page_content="functools.wraps 可以保留被裝飾函式的 metadata。"),
    Document(page_content="Java 的 Spring Boot 框架常用於企業級應用開發。"),
]

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# === 2. 建立 EmbeddingsFilter ===
embeddings_filter = EmbeddingsFilter(
    embeddings=embeddings,
    similarity_threshold=0.75  # 只保留相似度 > 0.75 的文件
)

# === 3. 建立 ContextualCompressionRetriever ===
compression_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,
    base_retriever=base_retriever
)

# === 4. 搜尋 ===
query = "怎麼寫 Python decorator？"
results = compression_retriever.invoke(query)

print(f"查詢：{query}")
print(f"過濾後剩下 {len(results)} 筆文件：\n")

for doc in results:
    print(f"  {doc.page_content}")
