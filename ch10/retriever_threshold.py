# ch10/retriever_threshold.py
"""Retriever 搜尋策略：similarity_score_threshold"""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ✅ 修復：補上 InMemoryVectorStore 缺少的 relevance score function
class PatchedInMemoryVectorStore(InMemoryVectorStore):
    def _select_relevance_score_fn(self):
        # InMemoryVectorStore 使用餘弦相似度，值域已是 [0, 1]，直接回傳即可
        return lambda score: score

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

documents = [
    Document(page_content="量子力學是研究微觀粒子行為的物理學分支。"),
    Document(page_content="Python 是一種程式語言。"),
    Document(page_content="台灣小吃種類繁多，夜市文化聞名世界。"),
]

# vector_store = InMemoryVectorStore.from_documents(documents, embeddings)
# ✅ 改用修補後的子類別
vector_store = PatchedInMemoryVectorStore.from_documents(documents, embeddings)

# 設定較高的閾值
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 3,
        "score_threshold": 0.65  # 門檻設為 0.65
    }
)

# 查詢跟文件庫高度相關的問題
query1 = "什麼是量子力學？"
results1 = retriever.invoke(query1)
print(f"🔍 「{query1}」→ 找到 {len(results1)} 筆")

for doc in results1:
    print(f"   📄 {doc.page_content}")

# 查詢跟文件庫不太相關的問題
query2 = "太空探索的最新進展"
results2 = retriever.invoke(query2)
print(f"\n🔍 「{query2}」→ 找到 {len(results2)} 筆")

if not results2:
    print("   ⚠️ 沒有找到足夠相關的文件（低於閾值）")
