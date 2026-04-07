# 檔案名稱：research_team.py

"""
AI 研究報告團隊
===============
使用 LangGraph 工作流，建立 Researcher → Writer → Reviewer 的報告產出流程。

本範例示範 LangChain 1.2+ 的重點：
1. create_agent 搭配 response_format 取得結構化輸出，避免 Gemini 在 tool use
   之後回傳空白 final message 的問題。
2. 使用 add_messages reducer，符合 LangGraph 官方建議且可被 checkpointer 序列化。
3. Mock 工具回傳帶出處的資料，讓整條鏈路(工具→研究員→作家→審核員)都有真實
   可追溯的來源,避免審核員因「無來源」陷入死迴圈。
"""

from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# ============================================
# 模型設定
# ============================================

model = init_chat_model("google_genai:gemini-2.5-flash")

# ============================================
# 結構化輸出 Schema
# ============================================

class ResearchReport(BaseModel):
    """研究員產出的結構化研究報告。"""
    summary: str = Field(description="研究摘要,約 100 字")
    findings: list[str] = Field(description="主要發現,至少 3 點")
    key_data: str = Field(description="關鍵數據與統計")
    conclusion: str = Field(description="研究結論")
    sources: list[str] = Field(
        description="所有引用的資料來源,包含機構、報告名稱、年份"
    )

class ReviewResult(BaseModel):
    """審核員的審核結果。"""
    is_approved: bool = Field(description="是否通過審核")
    feedback: str = Field(description="具體的審核評語或修改建議")

# ============================================
# 定義共享狀態
# ============================================

class ReportState(TypedDict):
    """報告團隊的共享狀態。"""
    messages: Annotated[list, add_messages]
    topic: str                    # 使用者指定的研究主題
    research_findings: str        # 研究員的發現(格式化後的字串)
    report_draft: str             # 作家的報告草稿
    review_feedback: str          # 審核員的回饋
    revision_count: int           # 修改次數
    is_approved: bool             # 是否通過審核
    final_report: str             # 最終報告


# ============================================
# 工具定義
# ============================================

@tool
def search_web(query: str) -> str:
    """搜尋網路上的最新資訊。"""
    # 在實際專案中,這裡應該接上真正的搜尋 API(如 Tavily、Serper)
    # 真實 API 會回傳帶 URL 的來源,這裡用 mock 模擬同樣的結構。
    return (
        f"搜尋 '{query}' 的結果:\n\n"
        f"[來源 1] McKinsey Global Institute (2026). "
        f"《The State of AI in the Enterprise 2026》\n"
        f"  - {query} 領域正在快速演進,企業採用率年增 45%。\n"
        f"  - 主要趨勢:自動化程度提升、成本降低、應用場景擴大。\n\n"
        f"[來源 2] IDC Worldwide AI Spending Guide (2026 年 3 月版)\n"
        f"  - 預估 2027 年全球 LLM 企業應用市場規模達 1500 億美元。\n"
        f"  - 複合年增長率(CAGR)為 38.2%。\n\n"
        f"[來源 3] Stanford HAI AI Index Report 2026\n"
        f"  - 關鍵挑戰:安全性、可解釋性、能源消耗。\n"
        f"  - 70% 受訪企業將「可解釋性」列為部署首要關切。"
    )

@tool
def search_papers(query: str) -> str:
    """搜尋學術論文和研究報告。"""
    return (
        f"學術搜尋 '{query}' 的結果:\n\n"
        f"[論文 A] Chen et al. (2026). "
        f"《Enterprise-Scale LLM Deployment: Advances and Challenges》. "
        f"Nature Machine Intelligence, 8(3), 214-231.\n"
        f"  摘要:系統性回顧 2024-2026 年企業 LLM 部署案例,"
        f"歸納出七大成功模式與三大失敗陷阱。\n\n"
        f"[論文 B] Kumar & Tanaka (2025). "
        f"《Practical Applications and Challenges of LLMs in Industry》. "
        f"ACM Computing Surveys, 57(12), Article 245.\n"
        f"  摘要:涵蓋金融、醫療、製造三大垂直領域的 LLM 實務應用分析。\n\n"
        f"[論文 C] Anthropic Research Team (2026). "
        f"《Towards Interpretable Enterprise AI》. arXiv:2601.12345.\n"
        f"  摘要:提出新型可解釋性框架,降低 LLM 黑箱問題對企業決策的影響。"
    )

# ============================================
# 建立 Agent
# ============================================

researcher = create_agent(
    model,
    tools=[search_web, search_papers],
    system_prompt=(
        "你是一位資深研究員,擅長深入調查各種主題。\n\n"
        "執行研究任務時,請:\n"
        "1. 使用 search_web 搜尋最新產業動態\n"
        "2. 使用 search_papers 搜尋學術研究\n"
        "3. 整合所有搜尋結果,產出結構化的研究報告\n\n"
        "你必須以 ResearchReport 的結構回覆,包含:\n"
        "- summary:研究摘要\n"
        "- findings:主要發現(至少 3 點)\n"
        "- key_data:關鍵數據\n"
        "- conclusion:研究結論\n"
        "- sources:資料來源清單\n\n"
        "⚠️ 重要:sources 欄位必須列出所有工具回傳中標註的來源"
        "(例如 McKinsey、IDC、Nature 論文等),"
        "不可自行編造,也不可留空。"
    ),
    response_format=ResearchReport,
    name="researcher",
)

writer = create_agent(
    model,
    tools=[],
    system_prompt=(
        "你是一位專業的技術報告作家。\n\n"
        "根據收到的研究資料,撰寫一篇正式的研究報告。\n"
        "報告格式要求:\n"
        "1. 標題\n"
        "2. 摘要(100-150 字)\n"
        "3. 引言\n"
        "4. 主要發現(分點論述)\n"
        "5. 分析與討論\n"
        "6. 結論與建議\n"
        "7. 參考文獻(列出研究資料中提供的所有來源)\n\n"
        "⚠️ 引用關鍵數據時,必須在句末標註來源,"
        "例如:(IDC, 2026)、(Chen et al., 2026)。\n"
        "⚠️ 只能引用【資料來源】段落中列出的來源,不可自行編造。\n\n"
        "寫作風格:專業但易讀,適合技術管理者閱讀。\n"
        "如果收到修改建議,請根據建議修改對應段落,並回覆完整的報告。"
    ),
    name="writer",
)

reviewer = create_agent(
    model,
    tools=[],
    system_prompt=(
        "你是一位嚴格但公正的品質審核員。\n\n"
        "審核報告的標準:\n"
        "1. 內容準確性:資訊是否正確、有無矛盾\n"
        "2. 結構完整性:是否包含所有必要段落(含參考文獻)\n"
        "3. 邏輯連貫性:論述是否有邏輯\n"
        "4. 可讀性:是否容易理解\n"
        "5. 專業度:用詞和表述是否專業\n"
        "6. 引用規範:關鍵數據是否標註具體來源(機構/作者+年份)\n\n"
        "注意:像 [某知名市場研究機構報告] 這類佔位符不算真正的資料來源。\n"
        "但若報告已引用具體的機構或論文(例如 IDC 2026、Chen et al. 2026),\n"
        "則視為合格的引用。\n\n"
        "你必須以 ReviewResult 的結構回覆:\n"
        "- is_approved:是否通過(布林值)\n"
        "- feedback:具體的評語或修改建議\n\n"
        "最多只會有 2 次修改機會,請提出具體可行的建議。"
    ),
    response_format=ReviewResult,
    name="reviewer",
)

# ============================================
# 輔助函式
# ============================================

def format_research_report(report: ResearchReport) -> str:
    """將結構化研究報告轉為給作家閱讀的字串。"""
    findings_text = "\n".join(
        f"  {i}. {f}" for i, f in enumerate(report.findings, 1)
    )
    sources_text = "\n".join(f"  - {s}" for s in report.sources)
    return (
        f"【研究摘要】\n{report.summary}\n\n"
        f"【主要發現】\n{findings_text}\n\n"
        f"【關鍵數據】\n{report.key_data}\n\n"
        f"【研究結論】\n{report.conclusion}\n\n"
        f"【資料來源】\n{sources_text}"
    )

# ============================================
# 定義工作流節點
# ============================================

def research_node(state: ReportState) -> dict:
    """研究節點:呼叫研究員進行資料收集。"""
    topic = state["topic"]
    print(f"\n🔍 研究員正在研究:{topic}")

    result = researcher.invoke(
        {"messages": [{"role": "user", "content": f"請深入研究以下主題:{topic}"}]}
    )

    # 透過 response_format 取得結構化輸出,
    # 避免 Gemini 在 tool use 後回傳空白 final message 的問題。
    report: ResearchReport = result["structured_response"]
    findings = format_research_report(report)

    print(f"✅ 研究完成(共 {len(findings)} 字,引用 {len(report.sources)} 個來源)")

    return {
        "research_findings": findings,
        "messages": [{"role": "assistant", "content": "[研究員] 研究報告已完成。"}],
    }

def writing_node(state: ReportState) -> dict:
    """寫作節點:呼叫作家撰寫報告。"""
    revision_count = state.get("revision_count", 0)
    research = state["research_findings"]
    feedback = state.get("review_feedback", "")

    if revision_count == 0:
        prompt = f"根據以下研究資料撰寫正式報告:\n\n{research}"
        print(f"\n✍️ 作家正在撰寫初稿...")
    else:
        old_draft = state["report_draft"]
        prompt = (
            f"請根據審核意見修改報告。\n\n"
            f"原始研究資料:\n{research}\n\n"
            f"目前報告:\n{old_draft}\n\n"
            f"審核意見:\n{feedback}\n\n"
            f"請修改後回覆完整的報告。"
        )
        print(f"\n✍️ 作家正在修改報告(第 {revision_count} 次修改)...")

    result = writer.invoke(
        {"messages": [{"role": "user", "content": prompt}]}
    )

    draft = result["messages"][-1].content
    stage = "初稿" if revision_count == 0 else "修改稿"
    print(f"✅ {stage}完成(共 {len(draft)} 字)")

    return {
        "report_draft": draft,
        "revision_count": revision_count + 1,
        "messages": [
            {"role": "assistant", "content": f"[作家] 報告{stage}已完成。"}
        ],
    }

def review_node(state: ReportState) -> dict:
    """審核節點:呼叫審核員檢查報告品質。"""
    draft = state["report_draft"]
    print(f"\n🔎 審核員正在審核報告...")

    result = reviewer.invoke(
        {"messages": [{"role": "user", "content": f"請審核以下報告:\n\n{draft}"}]}
    )

    # 使用結構化輸出取得審核結果,比字串前綴判斷更穩定
    review: ReviewResult = result["structured_response"]

    if review.is_approved:
        print(f"✅ 審核通過!")
    else:
        print(f"🔄 審核未通過,需要修改。")

    return {
        "review_feedback": review.feedback,
        "is_approved": review.is_approved,
        "final_report": draft if review.is_approved else "",
        "messages": [
            {
                "role": "assistant",
                "content": f"[審核員] {'✅ 通過' if review.is_approved else '❌ 需修改'}",
            }
        ],
    }

# ============================================
# 路由邏輯
# ============================================

def after_review(state: ReportState) -> Literal["writing", "end"]:
    """審核後的路由決策。"""
    if state.get("is_approved", False):
        return "end"

    # 最多修改 2 次(初稿 + 2 次修改 = 共 3 次寫作),超過就強制通過
    if state.get("revision_count", 0) >= 3:
        print("⚠️ 已達最大修改次數,強制完成。")
        return "end"

    return "writing"

# ============================================
# 組裝工作流
# ============================================

workflow = StateGraph(ReportState)

workflow.add_node("research", research_node)
workflow.add_node("writing", writing_node)
workflow.add_node("review", review_node)

workflow.add_edge(START, "research")
workflow.add_edge("research", "writing")
workflow.add_edge("writing", "review")

workflow.add_conditional_edges(
    "review",
    after_review,
    {"writing": "writing", "end": END},
)

checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# ============================================
# 主程式
# ============================================

def main():
    """執行研究報告團隊。"""
    topic = "2026 年大型語言模型(LLM)在企業應用中的發展趨勢"

    print("=" * 60)
    print("🚀 AI 研究報告團隊啟動")
    print(f"📋 研究主題:{topic}")
    print("=" * 60)

    config = {"configurable": {"thread_id": "report-001"}}

    result = app.invoke(
        {
            "messages": [],
            "topic": topic,
            "research_findings": "",
            "report_draft": "",
            "review_feedback": "",
            "revision_count": 0,
            "is_approved": False,
            "final_report": "",
        },
        config,
    )

    print("\n" + "=" * 60)
    print("📊 工作流程結束")
    print("=" * 60)
    print(f"修改次數:{result['revision_count'] - 1}")
    print(f"審核結果:{'✅ 通過' if result['is_approved'] else '⚠️ 強制完成'}")

    print("\n" + "=" * 60)
    print("📚 研究員的研究發現")
    print("=" * 60)
    print(result["research_findings"])

    print("\n" + "=" * 60)
    print("📄 最終報告")
    print("=" * 60)
    print(result["final_report"] or result["report_draft"])

    print("\n" + "=" * 60)
    print("💬 審核員評語")
    print("=" * 60)
    print(result["review_feedback"])

if __name__ == "__main__":
    main()