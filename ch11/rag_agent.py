# 檔案名稱：rag_agent.py
# 功能：使用 create_agent 建立 RAG Agent，讓 LLM 自主決定何時搜尋

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

# === 1. 準備知識庫 ===
documents = [
    Document(page_content="""LangChain v1 核心變革：
- create_agent 取代舊的 create_react_agent
- Middleware 系統提供六大 Hook
- LCEL (pipe operator) 已淘汰
- Content Blocks 標準化輸出格式
- 底層使用 LangGraph runtime""",
        metadata={"source": "langchain_v1_overview.md"}),
    Document(page_content="""create_agent 參數說明：
- model：LLM 模型（可用 init_chat_model 初始化）
- tools：工具列表（@tool 裝飾器、BaseTool、MCP Tools）
- system_prompt：系統提示（字串或 SystemMessage）
- middleware：中介軟體列表
- response_format：結構化輸出格式
- checkpointer：狀態持久化""",
        metadata={"source": "create_agent_api.md"}),
    Document(page_content="""Middleware 六大 Hook：
1. before_agent：Agent 開始前觸發
2. before_model：送往 LLM 前觸發
3. modify_model_request：修改 LLM 請求
4. after_model：LLM 回覆後觸發
5. wrap_model_call：包裝整個 LLM 呼叫
6. wrap_tool_call：包裝工具呼叫""",
        metadata={"source": "middleware_guide.md"}),
    Document(page_content="""init_chat_model 使用方式：
使用 "provider:model" 格式字串初始化模型。
範例：
- "google_genai:gemini-2.5-flash"
- "anthropic:claude-sonnet-4-6"
支援參數：temperature、max_tokens 等。
來自 langchain.chat_models 模組。""",
        metadata={"source": "init_chat_model_guide.md"}),
    Document(page_content="""Checkpointer 狀態持久化：
MemorySaver 提供記憶體內的狀態存儲，適合開發測試。
PostgresSaver 提供 PostgreSQL 持久化，適合生產環境。
使用 checkpointer 後，Agent 可以記住跨多輪的對話歷史。
每個對話使用 thread_id 區分不同的會話。""",
        metadata={"source": "checkpointer_guide.md"}),
]

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# === 2. 把 Retriever 包裝成 Tool ===

@tool
def search_langchain_docs(query: str) -> str:
    """搜尋 LangChain 技術文件知識庫。
    當使用者詢問 LangChain 相關的技術問題時，使用此工具搜尋。
    輸入應該是與問題相關的搜尋關鍵字。
    """

    docs = retriever.invoke(query)

    if not docs:
        return "未找到相關文件。"

    results = []

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知")
        results.append(f"[文件 {i}]（來源：{source}）\n{doc.page_content}")

    return "\n\n".join(results)

# === 3. 建立 RAG Agent ===
llm = init_chat_model("google_genai:gemini-2.5-flash")

agent = create_agent(
    model=llm,
    tools=[search_langchain_docs],
    system_prompt="""你是一位 LangChain 技術文件助理。
你的任務是回答使用者關於 LangChain v1 的技術問題。
規則：
1. 當使用者問技術問題時，先使用搜尋工具查詢知識庫
2. 根據搜尋結果回答問題，並標注資訊來源
3. 如果搜尋結果不足以回答，可以再搜一次用不同的關鍵字
4. 如果知識庫中沒有相關資訊，誠實告知使用者
5. 對於閒聊（如打招呼、感謝），直接回覆，不需要搜尋"""
)

# === 輔助函式：從 Content Blocks 提取文字 ===

def extract_text(content):
    """從 Content Blocks 或純字串中提取文字。
    LangChain 1.2+ 使用 Content Blocks 標準化格式，
    當 Agent 呼叫工具後回覆時，content 會是 list[dict]，
    而非單純的 str。此函式統一處理兩種情況。
    """
    if isinstance(content, str):
        return content
    # Content Blocks 格式：list of dict
    return "\n".join(
        block["text"] for block in content if block.get("type") == "text"
    )

# === 4. 測試 RAG Agent ===
# 測試 1：技術問題 → Agent 應該會搜尋

print("=== 測試 1：技術問題 ===")

result = agent.invoke(
    {"messages": [{"role": "user", "content": "create_agent 有哪些參數？"}]}
)

for msg in reversed(result["messages"]):
    if msg.type == "ai" and msg.content:
        print(f"Agent 回覆：{extract_text(msg.content)}")
        break

print("\n" + "=" * 50)

# 測試 2：閒聊 → Agent 不應該搜尋
print("\n=== 測試 2：閒聊 ===")

result = agent.invoke(
    {"messages": [{"role": "user", "content": "你好啊！"}]}
)

for msg in reversed(result["messages"]):
    if msg.type == "ai" and msg.content:
        print(f"Agent 回覆：{extract_text(msg.content)}")
        break

print("\n" + "=" * 50)

# 測試 3：需要多次搜尋的複雜問題

print("\n=== 測試 3：複雜問題 ===")

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Middleware 有哪些 Hook？怎麼搭配 Checkpointer 使用？"}]}
)

for msg in reversed(result["messages"]):
    if msg.type == "ai" and msg.content:
        print(f"Agent 回覆：{extract_text(msg.content)}")
        break