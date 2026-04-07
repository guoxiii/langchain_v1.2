# citation_agent.py

"""帶引用追蹤的問答 Agent"""

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.tools import tool
from src.hybrid_retriever import HybridRetriever
from src.config import PRIMARY_MODEL

# ── 定義結構化輸出格式 ──

class Citation(BaseModel):
    """單一引用來源"""
    source_file: str = Field(description="來源檔案名稱或 URL")
    page_or_chunk: str = Field(description="頁碼或段落編號")

    relevant_text: str = Field(
        description="支持回答的原文片段（簡短摘要）"
    )

class AnswerWithCitations(BaseModel):
    """帶引用的回答"""
    answer: str = Field(description="對使用者問題的完整回答")

    citations: list[Citation] = Field(
        description="支持回答的引用來源列表",
        default_factory=list,
    )

    confidence: str = Field(
        description="回答的信心程度：high / medium / low",
        default="medium",
    )

# ── 全域的 Retriever 實例 ──
# 在實際應用中，這會在應用啟動時初始化
retriever: HybridRetriever | None = None

def init_retriever(chunks: list[Document] | None = None):
    """初始化全域 Retriever。"""
    global retriever
    retriever = HybridRetriever(all_chunks=chunks)

# ── 搜尋工具工廠 ──
def create_search_tool(user_access_level: str = "public"):
    """
    依使用者權限建立搜尋工具。

    用閉包（closure）把 user_access_level 綁進工具內部，
    這樣 LLM 呼叫工具時不需要自己判斷權限等級。
    """

    @tool
    def search_documents(query: str) -> str:
        """
        搜尋企業文件知識庫。
        使用這個工具來查找與使用者問題相關的文件內容。
        它會同時搜尋向量資料庫、知識圖譜和關鍵字索引，
        回傳最相關的文件片段及其來源資訊。

        Args:
            query: 要搜尋的問題或關鍵字

        Returns:
            搜尋結果，包含文件內容和來源資訊
        """

        if retriever is None:
            return "錯誤：檢索器尚未初始化。"

        results = retriever.retrieve(
            query=query,
            user_access_level=user_access_level,
        )

        if not results:
            return "未找到相關文件。"

        # 格式化結果，包含來源資訊
        formatted = []

        for i, doc in enumerate(results, 1):
            source = doc.metadata.get(
                "file_name",
                doc.metadata.get("source_url", "未知來源"),
            )

            chunk_idx = doc.metadata.get("chunk_index", "N/A")

            retrieval_method = doc.metadata.get(
                "retrieval_method", "unknown"
            )

            formatted.append(
                f"[來源 {i}] 檔案：{source} | "
                f"段落：{chunk_idx} | "
                f"檢索方式：{retrieval_method}\n"
                f"內容：{doc.page_content}\n"
            )

        return "\n---\n".join(formatted)

    return search_documents

# ── 建立 Agent ──
def create_doc_qa_agent(user_access_level: str = "public"):
    """
    建立企業文件問答 Agent。
    這個 Agent 具備：
    - 文件搜尋能力（依使用者權限過濾）
    - 結構化輸出（帶引用的回答）
    - 系統提示詞引導
    """
    model = init_chat_model(PRIMARY_MODEL)

    system_prompt = """你是一個企業知識庫助理。你的職責是根據企業內部文件，
準確回答使用者的問題。

重要規則：
1. **必須先搜尋**：在回答任何問題之前，先使用 search_documents 工具搜尋相關文件。
2. **基於事實**：你的回答必須完全基於搜尋到的文件內容，不要編造資訊。
3. **附帶引用**：每個重要的陳述都必須標注來源（哪個檔案、哪個段落）。
4. **承認不知道**：如果搜尋結果中找不到答案，誠實地說「根據目前的文件庫，我無法找到相關資訊」。
5. **使用繁體中文**回答。

回答格式示例：
「根據《員工手冊》第 3 段，公司的年假政策為：新進員工滿一年可享有 7 天年假 [來源 1]。

此外，主管級以上員工可享有 14 天年假 [來源 2]。」
"""

    # 用工廠函式建立綁定了權限的搜尋工具
    search_tool = create_search_tool(user_access_level)

    agent = create_agent(
        model=model,
        tools=[search_tool],
        system_prompt=system_prompt,
        response_format=AnswerWithCitations,
    )

    return agent

# ── 使用範例 ──
def ask_question(
    agent,
    question: str,
    thread_id: str = "default",
):
    """
    向 Agent 提問並取得帶引用的回答。
    """
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}},
    )

    # 從結構化回應中取得結果
    structured = result.get("structured_response")

    if structured:
        print(f"\n📝 回答：\n{structured.answer}\n")

        if structured.citations:
            print("📚 引用來源：")

            for i, cite in enumerate(structured.citations, 1):
                print(
                    f"   [{i}] {cite.source_file} "
                    f"(段落 {cite.page_or_chunk})"
                )

                print(f"       摘要：{cite.relevant_text}")

        print(f"\n🎯 信心程度：{structured.confidence}")
    else:
        # 如果結構化輸出失敗，回退到純文字
        last_msg = result["messages"][-1]
        print(f"\n📝 回答：\n{last_msg.content}")

    return result

if __name__ == "__main__":
    # 快速測試
    from src.document_pipeline import DocumentPipeline

    # 1. 處理文件
    pipeline = DocumentPipeline()

    chunks = pipeline.process([
        {
            "source": "docs/employee_handbook.pdf",
            "department": "hr",
            "access_level": "internal",
        },
    ])

    # 2. 建立向量存儲
    from src.vector_store import VectorStoreManager

    vs = VectorStoreManager()
    vs.add_documents(chunks)

    # 3. 初始化 Retriever
    init_retriever(chunks)

    # 4. 建立 Agent 並提問（預設 public 權限）
    agent = create_doc_qa_agent(user_access_level="internal")

    ask_question(agent, "公司的年假政策是什麼？")
