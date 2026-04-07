# ch17_practice/rag_agent_traced.py

"""建立一個帶有 LangSmith 追蹤的 RAG Agent"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable

# 載入環境變數
load_dotenv()

# ========== 建立 RAG 知識庫 ==========
@traceable(name="build_knowledge_base")
def build_knowledge_base() -> InMemoryVectorStore:
    """讀取 FAQ 文件並建立向量知識庫"""
    # 讀取文件
    with open("documents/faq.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # 切割文件
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", "，", " "],
    )

    docs = text_splitter.create_documents(
        texts=[content],
        metadatas=[{"source": "faq.txt"}],
    )

    print(f"📄 文件已切割為 {len(docs)} 個 chunk")

    # 建立 Embedding 和 Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vector_store = InMemoryVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
    )

    print("✅ 向量知識庫建立完成")

    return vector_store

# ========== 建立搜尋工具 ==========
# 全域變數：知識庫
vector_store = None

@tool
def search_faq(query: str) -> str:
    """搜尋 TechBook 科技書店的 FAQ 知識庫。
    當使用者詢問關於營業時間、退換貨、會員制度、運費、付款方式、
    配送時間等問題時，使用此工具搜尋相關資訊。
    """
    global vector_store

    if vector_store is None:
        return "知識庫尚未初始化"

    # 搜尋最相關的 3 個 chunk
    results = vector_store.similarity_search(query, k=3)

    if not results:
        return "在知識庫中找不到相關資訊"

    # 將搜尋結果組合成文字
    context = "\n---\n".join([doc.page_content for doc in results])
    return f"以下是從知識庫中找到的相關資訊：\n{context}"

# ========== 建立並執行 Agent ==========
def main():
    global vector_store

    # 建立知識庫
    vector_store = build_knowledge_base()

    # 初始化模型
    llm = init_chat_model("google_genai:gemini-2.5-flash")

    # 建立 Agent
    agent = create_agent(
        model=llm,
        tools=[search_faq],
        system_prompt=(
            "你是 TechBook 科技書店的客服助手。"
            "請使用 search_faq 工具來回答客戶的問題。"
            "回覆時請親切有禮，並提供準確的資訊。"
            "如果在知識庫中找不到答案，請誠實告知客戶。"
        ),
    )

    # 測試查詢
    test_questions = [
        "你們週日有開嗎？",
        "我想退貨，要怎麼處理？",
        "買多少錢免運費？可以用 LINE Pay 嗎？",
        "你們有賣筆電嗎？",  # FAQ 中沒有的問題
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"📝 使用者問題：{question}")
        print(f"{'='*60}")

        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={
                "metadata": {
                    "test_category": "faq",
                    "question": question,
                },
                "tags": ["ch17-practice", "rag-agent"],
                "run_name": f"FAQ查詢: {question[:20]}",
            },
        )

        # 印出 Agent 的最終回覆
        final_message = result["messages"][-1]

        if hasattr(final_message, "content"):
            print(f"\n🤖 Agent 回覆：\n{final_message.content}")

if __name__ == "__main__":
    main()
