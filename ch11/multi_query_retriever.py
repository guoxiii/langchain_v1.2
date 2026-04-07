# 檔案名稱：multi_query_retriever.py
# 功能：使用 MultiQueryRetriever 從多角度搜尋文件
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_classic.retrievers.multi_query import MultiQueryRetriever

import logging

# 開啟日誌，觀察生成的查詢
logging.basicConfig()
logging.getLogger("langchain_classic.retrievers.multi_query").setLevel(logging.INFO)

# === 1. 準備測試資料 ===
documents = [
    Document(page_content="LangChain 的 Agent 使用 ReAct 迴圈來執行任務。Agent 會先思考（Reason），然後決定要使用哪個工具（Act），接著觀察工具回傳的結果（Observe），再決定下一步。"),
    Document(page_content="create_agent 是 LangChain v1 的核心函式，用來建立 AI Agent。它取代了舊版的 create_react_agent，底層使用 LangGraph runtime。"),
    Document(page_content="Middleware 是 LangChain v1 最重要的新功能之一。它提供 before_model、after_model 等 Hook，讓你可以在 Agent 執行的各個階段插入自定義邏輯。"),
    Document(page_content="ModelRetryMiddleware 提供指數退避重試機制。當 LLM API 呼叫失敗時，它會自動重試，並且每次重試之間的等待時間會指數增長，避免打爆 API。"),
    Document(page_content="handle_tool_error 參數可以設定為 True、字串、或自定義函式。當設為 True 時，工具的錯誤訊息會直接傳回給 Agent，讓 Agent 決定如何處理。"),
    Document(page_content="LangSmith 提供完整的追蹤功能，可以記錄每一次 LLM 呼叫、工具使用、和 Retriever 搜尋的詳細資訊，方便除錯和效能優化。"),
]

# === 2. 建立 Vector Store ===
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# === 3. 建立 Multi-Query Retriever ===
llm = init_chat_model("google_genai:gemini-2.5-flash")

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm,
    include_original=True  # 同時包含原始查詢
)

# === 4. 執行搜尋 ===
query = "Agent 出錯怎麼辦？"
results = multi_query_retriever.invoke(query)

print(f"\n查詢：{query}")
print(f"搜尋到 {len(results)} 筆不重複的文件：")

for i, doc in enumerate(results, 1):
    print(f"\n  [{i}] {doc.page_content[:80]}...")