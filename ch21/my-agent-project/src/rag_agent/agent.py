# src/rag_agent/agent.py

"""可部署的 RAG Agent — 具備文件檢索能力"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

# ===== 建立向量資料庫（範例用，實際專案使用持久化的 Vector Store）=====
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore(embedding=embeddings)

# 載入範例文件
sample_docs = [
    Document(
        page_content="LangGraph Platform 是 LangChain 的 Agent 部署平台，"
                     "它取代了已淘汰的 LangServe。提供 REST API、視覺化除錯、"
                     "背景執行、排程任務等功能。",
        metadata={"source": "langchain-docs", "topic": "deployment"},
    ),
    Document(
        page_content="LangGraph 使用 StateGraph 來定義有狀態的工作流。"
                     "核心概念包括 Node（節點）、Edge（邊）、State（狀態）。"
                     "它基於 Pregel/BSP 模型實現確定性並發。",
        metadata={"source": "langchain-docs", "topic": "langgraph"},
    ),
    Document(
        page_content="Middleware 是 LangChain v1 的核心功能，提供六大 Hook："
                     "before_agent、before_model、modify_model_request、"
                     "after_model、after_agent、wrap_model_call、wrap_tool_call。",
        metadata={"source": "langchain-docs", "topic": "middleware"},
    ),
    Document(
        page_content="RAG（檢索增強生成）是一種將外部知識注入 LLM 的技術。"
                     "流程包括：文件載入 → 文字切割 → 向量化 → 儲存 → 檢索 → 生成。",
        metadata={"source": "langchain-docs", "topic": "rag"},
    ),
    Document(
        page_content="create_agent 來自 langchain.agents，是 LangChain v1 的"
                     "核心 Agent 建構函式。它取代了舊版的 create_react_agent，"
                     "底層使用 LangGraph runtime，回傳 CompiledStateGraph。",
        metadata={"source": "langchain-docs", "topic": "agent"},
    ),
]

vectorstore.add_documents(sample_docs)

# ===== 定義 Retriever 工具 =====
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def search_knowledge_base(query: str) -> str:
    """搜尋知識庫中的技術文件。當使用者詢問 LangChain、LangGraph、
    RAG、Agent、Middleware 等技術問題時使用此工具。"""
    docs = retriever.invoke(query)

    if not docs:
        return "知識庫中沒有找到相關資料。"

    results = []

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        topic = doc.metadata.get("topic", "general")
        results.append(
            f"[資料 {i}] (來源: {source}, 主題: {topic})\n{doc.page_content}"
        )

    return "\n\n".join(results)


@tool
def get_current_time() -> str:
    """取得當前的日期和時間。"""
    from datetime import datetime
    now = datetime.now()
    return f"目前時間：{now.strftime('%Y 年 %m 月 %d 日 %H:%M:%S')}"

# ===== 建立 Agent =====
model = init_chat_model("anthropic:claude-sonnet-4-6")

graph = create_agent(
    model=model,
    tools=[search_knowledge_base, get_current_time],
    system_prompt=(
        "你是一位專業的 LangChain 技術助理。\n"
        "你的任務是回答使用者關於 LangChain、LangGraph、RAG、Agent 等技術問題。\n\n"
        "回答規則：\n"
        "1. 先使用 search_knowledge_base 工具查詢知識庫\n"
        "2. 根據查詢結果回答問題，並標注資料來源\n"
        "3. 如果知識庫中沒有相關資料，坦誠告知使用者\n"
        "4. 使用繁體中文回答\n"
        "5. 保持專業但友善的語氣"
    ),
)
