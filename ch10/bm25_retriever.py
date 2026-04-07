# ch10/bm25_retriever.py
"""BM25 關鍵字搜尋"""
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

documents = [
    Document(page_content="LangChain 的 create_agent 函式用於建立 AI Agent。", metadata={"source": "api_ref"}),
    Document(page_content="AI Agent 能夠自主決策並使用工具完成任務。", metadata={"source": "concept"}),
    Document(page_content="create_agent 接受 model、tools、prompt 等參數。", metadata={"source": "api_ref"}),
    Document(page_content="LangGraph 是 LangChain 底層的狀態機框架。", metadata={"source": "architecture"}),
]

# 建立 BM25 Retriever
bm25_retriever = BM25Retriever.from_documents(documents, k=2)

# 關鍵字搜尋
query = "create_agent 參數"
results = bm25_retriever.invoke(query)
print(f"🔍 BM25 搜尋：「{query}」\n")

for doc in results:
    print(f"  📄 {doc.page_content}")
    print(f"     來源：{doc.metadata['source']}\n")
