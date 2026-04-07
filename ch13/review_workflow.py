# 檔案名稱：review_workflow.py

"""
實作練習：文件審核工作流
結合 State、Node、Edge、條件邊、LLM、Checkpointer 的完整範例
"""

from dotenv import load_dotenv
load_dotenv()

from typing import Literal, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

# ============================================================
# 第一步：定義 State
# ============================================================

class ReviewState(TypedDict):
    """審核工作流的狀態"""
    document_title: str        # 文件標題
    document_content: str      # 文件內容
    reviewer_comments: str     # 審查意見
    decision: str              # 審查決定：approved / rejected
    final_message: str         # 最終通知訊息
    submission_count: int      # 提交次數

# ============================================================
# 第二步：初始化 LLM
# ============================================================

llm = init_chat_model("google_genai:gemini-2.5-flash")

# ============================================================
# 第三步：定義各個 Node
# ============================================================

def submit_document(state: ReviewState) -> dict:
    """提交文件節點"""
    count = state.get("submission_count", 0) + 1
    print(f"📄 文件「{state['document_title']}」已提交（第 {count} 次）")
    return {"submission_count": count}

def ai_review(state: ReviewState) -> dict:
    """AI 審查節點 — 使用 LLM 進行初步審查"""
    system_prompt = """你是一位文件審查員。請審查以下文件，並：
1. 給出審查意見（簡短說明優缺點）
2. 給出決定：如果文件品質良好，回答「APPROVED」；如果需要修改，回答「REJECTED」

請按照以下格式回答：
審查意見：（你的意見）

決定：APPROVED 或 REJECTED"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"文件標題：{state['document_title']}\n\n文件內容：{state['document_content']}")
    ])    

    response_text = response.content    

    # 解析 LLM 的回覆
    if "APPROVED" in response_text.upper():
        decision = "approved"
    else:
        decision = "rejected"    

    print(f"🔍 AI 審查完成，決定：{decision}")    

    return {
        "reviewer_comments": response_text,
        "decision": decision,
    }

def approve_document(state: ReviewState) -> dict:
    """核准節點"""
    message = (
        f"✅ 恭喜！您的文件「{state['document_title']}」已通過審核！\n"
        f"審查意見：{state['reviewer_comments']}"
    )

    print(message)
    return {"final_message": message}

def reject_document(state: ReviewState) -> dict:
    """退回節點"""
    message = (
        f"❌ 您的文件「{state['document_title']}」需要修改。\n"
        f"審查意見：{state['reviewer_comments']}\n"
        f"請根據意見修改後重新提交。"
    )

    print(message)
    return {"final_message": message}

# ============================================================
# 第四步：定義路由函式
# ============================================================

def route_decision(state: ReviewState) -> Literal["approve", "reject"]:
    """根據審查決定，路由到核准或退回節點"""
    if state["decision"] == "approved":
        return "approve"
    else:
        return "reject"

# ============================================================
# 第五步：建立圖
# ============================================================

graph_builder = StateGraph(ReviewState)

# 加入節點
graph_builder.add_node("submit", submit_document)
graph_builder.add_node("review", ai_review)
graph_builder.add_node("approve", approve_document)
graph_builder.add_node("reject", reject_document)

# 定義邊
graph_builder.add_edge(START, "submit")
graph_builder.add_edge("submit", "review")

# 條件邊：review 之後根據決定分流
graph_builder.add_conditional_edges(
    "review",
    route_decision,
    {
        "approve": "approve",
        "reject": "reject",
    }
)

# 兩個出口
graph_builder.add_edge("approve", END)
graph_builder.add_edge("reject", END)

# ============================================================
# 第六步：編譯（加入 Checkpointer）
# ============================================================

checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

# ============================================================
# 第七步：視覺化圖的結構
# ============================================================

print("=" * 60)
print("📊 工作流結構（Mermaid 語法）：")
print("=" * 60)
print(graph.get_graph().draw_mermaid())
print()

# ============================================================
# 第八步：執行工作流
# ============================================================

print("=" * 60)
print("🚀 開始執行審核工作流")
print("=" * 60)

# 情境一：提交一份品質良好的文件
config1 = {"configurable": {"thread_id": "review-001"}}
result1 = graph.invoke(
    {
        "document_title": "2025 年度技術報告",
        "document_content": """
本報告詳細分析了公司在 2025 年的技術發展方向。
主要內容包括：
1. AI 技術應用現況與未來規劃
2. 基礎設施升級時程
3. 團隊擴編計畫
4. 預算分配與 ROI 分析
每個章節都附有詳細的數據和圖表佐證。
        """.strip(),
        "submission_count": 0,
    },
    config=config1,
)

print(f"\n最終結果：{result1['final_message'][:50]}...")
print("\n" + "=" * 60)

# 情境二：提交一份過於簡略的文件
config2 = {"configurable": {"thread_id": "review-002"}}

result2 = graph.invoke(
    {
        "document_title": "月報",
        "document_content": "這個月還好。",
        "submission_count": 0,
    },
    config=config2,
)

print(f"\n最終結果：{result2['final_message'][:50]}...")

# 查看 checkpoint 狀態
print("\n" + "=" * 60)
print("📦 Checkpoint 狀態：")
print("=" * 60)

state = graph.get_state(config1)
print(f"Thread review-001 的決定：{state.values.get('decision')}")

state2 = graph.get_state(config2)
print(f"Thread review-002 的決定：{state2.values.get('decision')}")
