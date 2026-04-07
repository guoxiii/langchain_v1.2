# 檔案名稱：visualization.py

"""
將 LangGraph 圖視覺化並儲存為檔案
"""

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class ReviewState(TypedDict):
    document: str
    review_result: str
    status: str

def submit(state: ReviewState) -> dict:
    return {"status": "submitted"}

def review(state: ReviewState) -> dict:
    return {"review_result": "reviewed", "status": "reviewed"}

def approve(state: ReviewState) -> dict:
    return {"status": "approved"}

def reject(state: ReviewState) -> dict:
    return {"status": "rejected"}

def check_review(state: ReviewState) -> Literal["approve", "reject"]:
    # 模擬審查結果
    if "good" in state.get("document", ""):
        return "approve"

    return "reject"

graph_builder = StateGraph(ReviewState)
graph_builder.add_node("submit", submit)
graph_builder.add_node("review", review)
graph_builder.add_node("approve", approve)
graph_builder.add_node("reject", reject)
graph_builder.add_edge(START, "submit")
graph_builder.add_edge("submit", "review")
graph_builder.add_conditional_edges(
    "review",
    check_review,
    {"approve": "approve", "reject": "reject"}
)
graph_builder.add_edge("approve", END)
graph_builder.add_edge("reject", END)
graph = graph_builder.compile()

# 方法一：印出 Mermaid 語法
mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)

# 方法二：儲存為 PNG 檔案
png_bytes = graph.get_graph().draw_mermaid_png()

with open("review_workflow.png", "wb") as f:
    f.write(png_bytes)

print("圖片已儲存為 review_workflow.png")
