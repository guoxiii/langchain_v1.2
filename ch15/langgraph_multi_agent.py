# 檔案名稱：langgraph_multi_agent.py

from typing import TypedDict, Annotated, Literal, Any
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# 最多進行幾輪審核：首稿 + 至多 (MAX_REVIEW_ROUNDS - 1) 次修訂
# 避免 LLM 反覆挑剔導致無限迴圈，是生產環境常見的安全網
MAX_REVIEW_ROUNDS = 3

# === 相容性工具：處理 Gemini thinking mode 的 content 格式 ===
def extract_text(content: Any) -> str:
    """從 LLM 回應中提取純文字內容。

    當使用 Gemini 2.5 系列模型（尤其是啟用 thinking mode 時），
    `message.content` 可能不是單純的字串，而是 list[dict] 形式的
    content blocks，格式類似：

        [{'type': 'text', 'text': '實際內容...', 'extras': {...}}]

    直接把它當字串使用會導致後續節點收到一團 Python repr 格式的雜訊。
    這個輔助函式會把所有 text 區塊拼接成乾淨的字串。

    這是 LangChain 1.2+ 搭配 Gemini 2.5 時的常見陷阱，
    寫跨模型 Agent 程式時務必加上類似的正規化邏輯。
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)

# === 定義共享 State ===
class WorkflowState(TypedDict):
    """研究 → 寫作 → 審核 工作流的共享狀態。"""
    messages: Annotated[list, add_messages]  # 使用官方推薦的 reducer
    topic: str                    # 研究主題
    research_result: str          # 研究結果
    article_draft: str            # 當前文章草稿（會被新版覆蓋）
    review_result: str            # 最近一次審核結果
    is_approved: bool             # 是否通過審核
    review_count: int             # 已進行的審核輪次

# === 建立各 Agent ===
@tool
def web_search(query: str) -> str:
    """搜尋網路資料。"""
    return (
        f"搜尋 '{query}' 的結果：此領域在 2025-2026 年間有顯著進展。"
        f"根據 Gartner 2025 報告，全球 AI Agent 市場規模預計從 2024 年的 51 億美元"
        f"成長至 2030 年的 471 億美元，年複合成長率達 44.8%。主要廠商包括 "
        f"Microsoft、Google、Anthropic、OpenAI 等，企業採用率在 2025 年已達 35%。"
    )

researcher = create_agent(
    model,
    tools=[web_search],
    system_prompt=(
        "你是研究員。請針對指定主題進行徹底的研究。"
        "在最終回覆中提供：1) 關鍵發現 2) 重要數據 3) 趨勢分析。"
        "務必引用具體數字與來源。"
    ),
    name="researcher",
)

writer = create_agent(
    model,
    tools=[],
    system_prompt=(
        "你是專業作家。你有兩種任務模式：\n\n"
        "【首稿模式】當只給你研究資料時，撰寫一篇結構完整、"
        "引人入勝的文章（約 300-500 字），包含標題、開頭、主體、結論。\n\n"
        "【修訂模式】當同時給你研究資料、前一版草稿與審核意見時，"
        "請依據審核意見逐點修訂前一版草稿，輸出完整的新版文章。"
        "修訂時務必針對審核員提到的每一項缺失做出實質改進，"
        "特別是補充具體數據與實例，不要只是換句話說。\n\n"
        "【重要輸出規範】無論哪種模式，都請直接輸出文章本體（從標題開始），"
        "不要加入任何開場白、說明、確認語或分隔線。禁止出現以下內容：\n"
        "- 『好的，以下是...』、『我已根據審核意見...』等應答語\n"
        "- 『---』、『===』等分隔線\n"
        "- 『以下是修訂後的文章：』等過渡說明\n"
        "你的回覆必須直接從文章標題（例如 '## XXX'）開始。"
    ),
    name="writer",
)

reviewer = create_agent(
    model,
    tools=[],
    system_prompt=(
        "你是嚴格但公正的品質審核員。你的目標是確保品質達到專業水準，"
        "而不是無限追求完美。\n\n"
        "審核項目：\n"
        "1. 內容準確性（是否有過度概括或模糊陳述？）\n"
        "2. 邏輯連貫性（段落銜接是否自然？）\n"
        "3. 可讀性（結構是否清晰？）\n"
        "4. 數據支撐（是否引用了具體數字、百分比或實例？）\n\n"
        "【審核原則】\n"
        "• 第一次審核時：除非文章在四個面向都達到基本水準，否則退回修改。"
        "特別嚴格檢查是否有足夠的具體數據支撐，空泛陳述必須退回。\n\n"
        "• 後續審核時：如果作家已根據上一次的意見做出實質改進"
        "（例如補充了具體數據、修正了結構問題），就應該通過。"
        "不要在已經大幅改進的稿件上挑剔細枝末節，例如特定詞彙選擇、"
        "單句是否略顯冗餘、數據來源的年份是否完美精確等。\n\n"
        "• 記住：如果每項主要指標都達標，就該通過。完美不是審核的目標，"
        "專業品質才是。\n\n"
        "【回覆格式】\n"
        "- 合格 → 以 'APPROVED:' 開頭，後接簡短評語說明優點。\n"
        "- 需修改 → 以 'REVISION:' 開頭，後接具體且可操作的修改建議，逐點列出。"
    ),
    name="reviewer",
)

# === 定義節點函式 ===
def research_node(state: WorkflowState) -> dict:
    """研究節點：呼叫研究員 Agent。"""
    topic = state["topic"]

    result = researcher.invoke(
        {"messages": [{"role": "user", "content": f"請研究以下主題：{topic}"}]}
    )

    # 使用 extract_text 處理可能的 list[dict] content 格式
    research_content = extract_text(result["messages"][-1].content)

    return {
        "research_result": research_content,
        "messages": [
            {"role": "assistant", "content": f"[研究完成] {research_content[:80]}..."}
        ],
    }

def writing_node(state: WorkflowState) -> dict:
    """寫作節點：首稿或根據審核意見修訂。

    這是 LangGraph 狀態共享的關鍵示範——下游節點不只讀取上游的原始輸入，
    還能讀取其他節點的輸出（前一稿、審核意見），實現真正的協作修訂。
    """
    research = state["research_result"]
    previous_draft = state.get("article_draft", "")
    review_feedback = state.get("review_result", "")
    is_revision = bool(previous_draft and review_feedback)

    if is_revision:
        # 修訂模式：帶入前一稿與審核意見
        user_msg = (
            f"請根據審核意見修訂以下文章。\n\n"
            f"【原始研究資料】\n{research}\n\n"
            f"【前一版草稿】\n{previous_draft}\n\n"
            f"【審核意見】\n{review_feedback}\n\n"
            f"請針對審核意見逐點改進，直接輸出修訂後的完整文章（從標題開始）。"
        )
    else:
        # 首稿模式
        user_msg = f"請根據以下研究資料撰寫文章：\n\n{research}"

    result = writer.invoke({"messages": [{"role": "user", "content": user_msg}]})
    draft = extract_text(result["messages"][-1].content)

    label = "文章修訂完成" if is_revision else "文章草稿完成"
    return {
        "article_draft": draft,
        "messages": [
            {"role": "assistant", "content": f"[{label}] {draft[:80]}..."}
        ],
    }

def review_node(state: WorkflowState) -> dict:
    """審核節點：呼叫審核員 Agent，並累計審核輪次。"""
    draft = state["article_draft"]
    current_round = state.get("review_count", 0) + 1

    result = reviewer.invoke(
        {"messages": [{"role": "user", "content": f"請審核以下文章：\n\n{draft}"}]}
    )

    review = extract_text(result["messages"][-1].content)
    is_approved = review.strip().startswith("APPROVED")

    return {
        "review_result": review,
        "is_approved": is_approved,
        "review_count": current_round,
        "messages": [
            {
                "role": "assistant",
                "content": f"[第 {current_round} 輪審核] {'✅ 通過' if is_approved else '❌ 需修改'}",
            }
        ],
    }

# === 定義路由邏輯 ===
def should_revise(state: WorkflowState) -> Literal["writing", "end"]:
    """審核後的路由：通過或達到審核輪次上限就結束，否則回去修改。"""
    # 情況 1：審核通過，直接結束
    if state.get("is_approved", False):
        return "end"

    # 情況 2：已達到最大審核輪次，強制結束（生產環境的安全網）
    if state.get("review_count", 0) >= MAX_REVIEW_ROUNDS:
        return "end"

    # 情況 3：還有機會修訂，回到寫作節點
    return "writing"

# === 組裝 Graph ===
workflow = StateGraph(WorkflowState)

# 新增節點
workflow.add_node("research", research_node)
workflow.add_node("writing", writing_node)
workflow.add_node("review", review_node)

# 定義邊（流程順序）
workflow.add_edge(START, "research")         # 開始 → 研究
workflow.add_edge("research", "writing")     # 研究 → 寫作
workflow.add_edge("writing", "review")       # 寫作 → 審核

# 條件邊：審核後決定下一步
workflow.add_conditional_edges(
    "review",
    should_revise,
    {
        "writing": "writing",   # 不通過且未達上限 → 回去修改
        "end": END,             # 通過 或 已達上限 → 結束
    },
)

# 編譯
checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# === 執行 ===
def main():
    config = {"configurable": {"thread_id": "workflow-001"}}

    result = app.invoke(
        {
            "messages": [],
            "topic": "2026 年 AI Agent 技術的最新發展趨勢",
            "research_result": "",
            "article_draft": "",
            "review_result": "",
            "is_approved": False,
            "review_count": 0,
        },
        config,
    )

    print("=" * 60)
    print("工作流程完成！")
    print("=" * 60)
    print(f"\n總審核輪次：{result['review_count']} 輪")

    if result["is_approved"]:
        final_status = "✅ 審核通過"
    else:
        final_status = f"⚠️ 達到最大輪次 ({MAX_REVIEW_ROUNDS}) 強制結束"
    print(f"最終狀態：{final_status}")

    print(f"\n最終審核評語：\n{result['review_result']}")
    print(f"\n最終文章：\n{result['article_draft']}")

    # 顯示整個工作流的訊息軌跡
    print("\n" + "=" * 60)
    print("工作流訊息軌跡：")
    print("=" * 60)
    for msg in result["messages"]:
        # add_messages 會把 dict 轉換成 BaseMessage 物件
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        # 保險起見，訊息軌跡也用 extract_text 處理一次
        print(f"  • {extract_text(content)}")

if __name__ == "__main__":
    main()