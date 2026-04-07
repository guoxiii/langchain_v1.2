# ch10/faiss_filter.py
"""FAISS Metadata 過濾搜尋"""
from dotenv import load_dotenv

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

documents = [
    Document(page_content="赤崁樓是荷蘭時期建造的城堡，現為國定古蹟。", metadata={"city": "台南", "type": "古蹟"}),
    Document(page_content="台北故宮是世界四大博物館之一。", metadata={"city": "台北", "type": "博物館"}),
    Document(page_content="安平老街充滿了傳統小吃和手工藝品。", metadata={"city": "台南", "type": "老街"}),
    Document(page_content="九份老街以芋圓和夜景聞名。", metadata={"city": "新北", "type": "老街"}),
    Document(page_content="台南孔廟是台灣第一座孔廟，歷史悠久。", metadata={"city": "台南", "type": "古蹟"}),
]

vector_store = FAISS.from_documents(documents, embeddings)

# 過濾：只搜尋台南的景點
query = "有什麼值得逛的地方？"

results = vector_store.similarity_search_with_score(
    query=query,
    k=3,
    filter={"city": "台南"}  # FAISS 用字典格式過濾
)

print(f"🔍 搜尋：「{query}」（僅限台南）\n")

for doc, score in results:
    print(f"  距離：{score:.4f}  📄 {doc.page_content}")
    print(f"          城市：{doc.metadata['city']}  類型：{doc.metadata['type']}\n")
