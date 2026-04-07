# 檔案名稱：subgraph_shared_state.py

from dotenv import load_dotenv
load_dotenv()

import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# === 共享狀態 ===
class SharedState(TypedDict):
    topic: str
    research_notes: Annotated[list[str], operator.add]  # 使用 reducer 合併列表
    final_report: str

# === 子圖：Research 模組 ===
def search_web(state: SharedState) -> dict:
    topic = state["topic"]
    print(f"🔍 搜尋網路：{topic}")
    return {"research_notes": [f"[網路] 找到關於 {topic} 的 3 篇文章"]}

def search_database(state: SharedState) -> dict:
    topic = state["topic"]
    print(f"🗄️ 搜尋資料庫：{topic}")
    return {"research_notes": [f"[資料庫] 找到關於 {topic} 的 5 筆記錄"]}

def summarize_research(state: SharedState) -> dict:
    notes = state["research_notes"]
    summary = f"研究摘要：共收集 {len(notes)} 項資料"
    print(f"📋 {summary}")
    return {"research_notes": [summary]}

# 建立子圖
research_graph = StateGraph(SharedState)
research_graph.add_node("search_web", search_web)
research_graph.add_node("search_database", search_database)
research_graph.add_node("summarize", summarize_research)
research_graph.add_edge(START, "search_web")
research_graph.add_edge(START, "search_database")  # search_web 和 search_database 平行執行
research_graph.add_edge("search_web", "summarize")
research_graph.add_edge("search_database", "summarize")
research_graph.add_edge("summarize", END)

# 編譯子圖（注意：子圖不需要自己的 checkpointer）
research_subgraph = research_graph.compile()

# === 父圖 ===
def write_report(state: SharedState) -> dict:
    notes = state["research_notes"]
    report = f"最終報告：基於 {len(notes)} 項研究成果，結論是..."
    print(f"📄 {report}")
    return {"final_report": report}

# 建立父圖
parent_graph = StateGraph(SharedState)
parent_graph.add_node("research", research_subgraph)  # 把子圖當成一個節點
parent_graph.add_node("write_report", write_report)
parent_graph.add_edge(START, "research")
parent_graph.add_edge("research", "write_report")
parent_graph.add_edge("write_report", END)

# 編譯父圖（checkpointer 在父圖上設定）
checkpointer = InMemorySaver()
app = parent_graph.compile(checkpointer=checkpointer)

# 執行
config = {"configurable": {"thread_id": "research-1"}}

result = app.invoke(
    {"topic": "LangChain 2026 發展趨勢", "research_notes": [], "final_report": ""},
    config=config
)

print(f"\n最終報告：{result['final_report']}")
