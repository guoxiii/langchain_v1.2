# 檔案名稱：stream.py

"""
串流輸出 — 即時觀察圖的執行過程
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class PipelineState(TypedDict):
    data: str
    step1_done: bool
    step2_done: bool

def step_1(state: PipelineState) -> dict:
    return {"data": state["data"].upper(), "step1_done": True}

def step_2(state: PipelineState) -> dict:
    return {"data": state["data"] + "!!!", "step2_done": True}

graph_builder = StateGraph(PipelineState)
graph_builder.add_node("step_1", step_1)
graph_builder.add_node("step_2", step_2)
graph_builder.add_edge(START, "step_1")
graph_builder.add_edge("step_1", "step_2")
graph_builder.add_edge("step_2", END)
graph = graph_builder.compile()

# 使用 stream 即時觀察
for event in graph.stream({"data": "hello langgraph"}):
    print(f"事件：{event}")
    print("---")
