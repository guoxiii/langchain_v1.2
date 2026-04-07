# ch10/inmemory_filter.py
"""InMemoryVectorStore 的 Metadata 過濾"""
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
    Document(id="1", page_content="赤崁樓是台南最著名的歷史古蹟之一。", metadata={"city": "台南"}),
    Document(id="2", page_content="台北故宮收藏了大量珍貴的中華文物。", metadata={"city": "台北"}),
    Document(id="3", page_content="安平古堡見證了台灣數百年的歷史變遷。", metadata={"city": "台南"}),
    Document(id="4", page_content="中正紀念堂是台北的重要地標。", metadata={"city": "台北"}),
]

vector_store.add_documents(documents=documents)

# 定義過濾函式：只搜尋台南的文件
def tainan_filter(doc: Document) -> bool:
    return doc.metadata.get("city") == "台南"

query = "歷史古蹟"

results = vector_store.similarity_search(
    query=query,
    k=2,
    filter=tainan_filter  # 只在台南範圍內搜尋
)

print(f"🔍 搜尋：「{query}」（僅限台南）\n")

for doc in results:
    print(f"  📄 {doc.page_content}")
    print(f"     城市：{doc.metadata['city']}\n")
