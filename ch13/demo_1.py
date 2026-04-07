# demo_1.py

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class ProcessState(TypedDict):
    raw_text: str
    cleaned_text: str
    word_count: int

# Node 1：清理文字
def clean_text(state: ProcessState) -> dict:
    """移除多餘空白和換行"""
    cleaned = " ".join(state["raw_text"].split())
    return {"cleaned_text": cleaned}

# Node 2：計算字數
def count_words(state: ProcessState) -> dict:
    """計算清理後的文字字數"""
    count = len(state["cleaned_text"].split())
    return {"word_count": count}

# 建立圖
graph_builder = StateGraph(ProcessState)
graph_builder.add_node("clean", clean_text)
graph_builder.add_node("count", count_words)
graph_builder.add_edge(START, "clean")
graph_builder.add_edge("clean", "count")
graph_builder.add_edge("count", END)
graph = graph_builder.compile()

result = graph.invoke({
    "raw_text": "  LangGraph   真的   很好用    "
})

print(result)

# {'raw_text': '  LangGraph   真的   很好用    ',
#  'cleaned_text': 'LangGraph 真的 很好用',
#  'word_count': 3}
