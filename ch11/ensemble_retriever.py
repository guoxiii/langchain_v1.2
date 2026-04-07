# 檔案名稱：ensemble_retriever.py
# 功能：混合向量搜尋和 BM25 關鍵字搜尋
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# === 1. 準備測試資料 ===
documents = [
    Document(page_content="LangChain v1.2 新增了 create_agent 函式，取代舊的 create_react_agent。"),
    Document(page_content="Middleware 系統提供 before_model 和 after_model 等六大 Hook。"),
    Document(page_content="MCP（Model Context Protocol）是標準化的工具連接協議。"),
    Document(page_content="RAG 系統使用向量搜尋來檢索相關文件，增強 LLM 的回答品質。"),
    Document(page_content="LangSmith 提供追蹤、評估和監控 LLM 應用的完整功能。"),
    Document(page_content="create_agent 的回傳值是 CompiledStateGraph，具備完整的 LangGraph 功能。"),
    Document(page_content="PIIMiddleware 可以偵測並遮蔽個人敏感資訊，支援 redact 和 block 策略。"),
]

# === 2. 建立兩個 Retriever ===
# Retriever 1：向量搜尋（語意理解）
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Retriever 2：BM25 關鍵字搜尋（精確匹配）
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 3

# === 3. 建立 Ensemble Retriever ===
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5]  # 各佔 50% 權重
)

# === 4. 搜尋測試 ===
query = "怎麼建立 Agent？"
results = ensemble_retriever.invoke(query)

print(f"查詢：{query}")
print(f"Ensemble 結果（{len(results)} 筆）：\n")

for i, doc in enumerate(results, 1):
    print(f"  [{i}] {doc.page_content}")
