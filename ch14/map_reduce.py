# 檔案名稱：map_reduce.py

from dotenv import load_dotenv
load_dotenv()

import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Send
from langchain.chat_models import init_chat_model

# 初始化模型
llm = init_chat_model("google_genai:gemini-2.5-flash")

# === 主圖的狀態 ===
class MainState(TypedDict):
    topic: str
    subtopics: list[str]
    summaries: Annotated[list[str], operator.add]  # 用 reducer 合併並行結果
    final_report: str

# === 並行工人的狀態（每個工人有自己的狀態）===
class WorkerState(TypedDict):
    subtopic: str
    summaries: Annotated[list[str], operator.add]

# --- 節點 1：分解主題 ---
def decompose_topic(state: MainState) -> dict:
    topic = state["topic"]
    response = llm.invoke(
        f"請將「{topic}」分解成 3 個子主題，"
        f"只回覆子主題名稱，用換行分隔，不要編號"
    )

    subtopics = [s.strip() for s in response.content.strip().split("\n") if s.strip()]
    print(f"📋 子主題：{subtopics}")
    return {"subtopics": subtopics}

# --- 節點 2：Map — 對每個子主題進行研究（並行）---
def research_subtopic(state: WorkerState) -> dict:
    subtopic = state["subtopic"]
    response = llm.invoke(
        f"請用 2-3 句話簡要說明「{subtopic}」的重點"
    )

    summary = f"【{subtopic}】{response.content.strip()}"
    print(f"🔍 完成研究：{subtopic}")
    return {"summaries": [summary]}

# --- 路由函式：動態建立並行任務 ---
def route_to_workers(state: MainState) -> list[Send]:
    """為每個子主題建立一個並行的 Send 任務"""
    return [
        Send(
            "research",  # 目標節點名稱
            {"subtopic": subtopic, "summaries": []}  # 每個工人的初始狀態
        )

        for subtopic in state["subtopics"]
    ]

# --- 節點 3：Reduce — 匯總所有研究結果 ---
def compile_report(state: MainState) -> dict:
    summaries = state["summaries"]
    report = f"📊 研究報告：{state['topic']}\n\n"

    for i, summary in enumerate(summaries, 1):
        report += f"{i}. {summary}\n\n"

    report += f"共涵蓋 {len(summaries)} 個子主題的研究。"
    print(report)
    return {"final_report": report}

# === 建立圖 ===
graph = StateGraph(MainState)
graph.add_node("decompose", decompose_topic)
graph.add_node("research", research_subtopic)  # 這個節點會被並行呼叫多次
graph.add_node("compile", compile_report)
graph.add_edge(START, "decompose")

# 關鍵：用 add_conditional_edges 搭配回傳 Send 列表
graph.add_conditional_edges(
    "decompose",
    route_to_workers,  # 這個函式回傳 Send 列表
    ["research"]       # 可能的目標節點
)

graph.add_edge("research", "compile")
graph.add_edge("compile", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# 執行
config = {"configurable": {"thread_id": "map-reduce-1"}}

result = app.invoke(
    {
        "topic": "Python 在 2026 年的發展趨勢",
        "subtopics": [],
        "summaries": [],
        "final_report": ""
    },
    config=config
)

print(f"\n{'=' * 50}")
print(result["final_report"])
