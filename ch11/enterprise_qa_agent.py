# 檔案名稱：enterprise_qa_agent.py
# 功能：整合進階 RAG 策略的企業文件問答系統

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter
from langchain_community.retrievers import BM25Retriever
from langgraph.checkpoint.memory import MemorySaver

# ============================================================
# 第一部分：建立知識庫與進階 Retriever
# ============================================================

# 企業文件（模擬）
company_docs = [
    Document(
        page_content="""員工特別休假管理辦法
第一條：員工到職滿六個月，即享有三天特別休假。
第二條：到職滿一年者，享有七天特別休假。
第三條：到職滿二年以上者，每增加一年加給一天，最多至十四天。
第四條：到職滿五年以上者，每增加一年加給一天，最多至三十天。
第五條：特別休假未休完者，可依勞基法規定折算工資。
第六條：特休申請需提前三個工作天，經主管核准後生效。""",
        metadata={"source": "人事管理辦法.pdf", "category": "人事"}
    ),
    Document(
        page_content="""加班費計算規則
一般工作日加班：前兩小時按時薪 1.34 倍計算，第三小時起按 1.67 倍。
休息日加班：前兩小時按時薪 1.34 倍，之後按 1.67 倍計算。
國定假日加班：全日按時薪 2 倍計算。
每月加班上限為 46 小時，經勞資會議同意可延長至 54 小時。
加班費於次月薪資一併發放。""",
        metadata={"source": "薪資管理辦法.pdf", "category": "薪資"}
    ),
    Document(
        page_content="""出差管理規定
國內出差：交通費實報實銷，每日膳雜費上限 800 元。
國外出差：需事前提出出差申請，經部門主管及總經理核准。
住宿標準：國內每晚上限 3,000 元，國外依目的地標準另訂。
出差報告須於返回後三個工作天內提交。
機票預訂統一由總務部處理。""",
        metadata={"source": "出差管理辦法.pdf", "category": "行政"}
    ),
    Document(
        page_content="""資訊安全管理規範
所有員工須使用公司配發的電腦處理公務。
密碼須至少 12 個字元，包含大小寫字母、數字和符號。
禁止使用個人 USB 隨身碟傳輸公司資料。
離開座位時須鎖定螢幕（Windows + L）。
發現資安事件須立即通報 IT 部門，通報信箱：security@company.com。
每季須完成一次資安教育訓練。""",
        metadata={"source": "資安管理規範.pdf", "category": "資安"}
    ),
    Document(
        page_content="""員工績效考核制度
績效等級分為 A（傑出）、B（優良）、C（合格）、D（待改善）。
年度考核期間為每年 1 月 1 日至 12 月 31 日。
考核項目包含：工作成果（40%）、專業能力（30%）、團隊合作（20%）、創新表現（10%）。
績效考核結果影響年終獎金：A 級 4 個月、B 級 3 個月、C 級 2 個月、D 級 0 個月。
績效面談由直屬主管於每年一月進行。""",
        metadata={"source": "績效考核辦法.pdf", "category": "人事"}
    ),
]

# 建立向量搜尋 Retriever
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(company_docs, embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 建立 BM25 關鍵字搜尋 Retriever
bm25_retriever = BM25Retriever.from_documents(company_docs)
bm25_retriever.k = 3

# 建立 Ensemble Retriever（混合搜尋）
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4]  # 語意搜尋權重略高
)

# 加上 Embedding 過濾器（Reranking）
embeddings_filter = EmbeddingsFilter(
    embeddings=embeddings,
    similarity_threshold=0.65
)

# 最終 Retriever：Ensemble + Reranking
final_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,
    base_retriever=ensemble_retriever
)

# ============================================================
# 第二部分：建立 RAG Agent
# ============================================================

@tool
def search_company_docs(query: str) -> str:
    """搜尋公司內部文件知識庫。
    可搜尋的文件範圍包括：人事管理辦法、薪資管理辦法、出差管理規定、
    資訊安全規範、績效考核制度等。
    輸入應為明確的搜尋關鍵字。
    """

    docs = final_retriever.invoke(query)

    if not docs:
        return "未找到相關的公司文件。請嘗試使用不同的關鍵字搜尋。"

    results = []

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知")
        category = doc.metadata.get("category", "未分類")

        results.append(
            f"[文件 {i}]（來源：{source}，類別：{category}）\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(results)

# 建立 Agent
llm = init_chat_model("google_genai:gemini-2.5-flash")

qa_agent = create_agent(
    model=llm,
    tools=[search_company_docs],
    system_prompt="""你是公司的 HR 智能助理「小幫手」。你的任務是回答員工關於公司制度的問題。

規則：
1. 收到技術問題時，使用 search_company_docs 工具搜尋公司文件
2. 回答必須基於搜尋到的文件內容，不要編造不在文件中的規定
3. 回答時標注資訊來源（文件名稱）
4. 如果搜尋結果不夠完整，可以用不同的關鍵字再搜一次
5. 如果文件中沒有相關規定，告知員工並建議聯繫 HR 部門
6. 保持友善、專業的語氣
7. 對於閒聊和打招呼，直接友善回覆""",
    checkpointer=MemorySaver()
)

# ============================================================
# 第三部分：測試對話
# ============================================================

def extract_text(content) -> str:
    """從 AI 回覆的 content 中提取純文字。
    處理 Gemini 模型可能回傳 list[dict] 的情況。
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = [
            block["text"] for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(parts) if parts else "（無回覆）"

    return str(content)

def chat(user_message: str, thread_id: str = "employee-001"):
    """與 QA Agent 對話"""
    config = {"configurable": {"thread_id": thread_id}}

    result = qa_agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config
    )

    # 取得最後一條 AI 回覆
    for msg in reversed(result["messages"]):
        if msg.type == "ai" and msg.content:
            return extract_text(msg.content)

    return "（無回覆）"

if __name__ == "__main__":
    # 對話測試
    print("=" * 60)
    print("企業文件 QA 系統 — 使用進階 RAG 策略")
    print("=" * 60)

    questions = [
        "你好，我是新進員工小明！",
        "我到職剛滿一年，有幾天特休？",
        "國定假日加班的加班費怎麼算？",
        "我要出差到日本，住宿費上限多少？",
        "密碼規定是什麼？要多少個字元？",
        "績效 A 級年終有幾個月？",
    ]

    for q in questions:
        print(f"\n👤 員工：{q}")
        answer = chat(q)
        print(f"🤖 小幫手：{answer}")
        print("-" * 40)