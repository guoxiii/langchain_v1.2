# 檔案名稱：reducer.py

"""
State Reducer 示範 — 理解狀態的合併方式
"""

from typing import Annotated
from typing_extensions import TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END

class CounterState(TypedDict):
    # 使用 operator.add 作為 reducer
    # 意思是：新值 = 舊值 + Node 回傳的值
    numbers: Annotated[list, add]  # list 的 add 就是 list 的串接
    total: int                      # 沒有 Annotated = 預設覆蓋

def add_numbers(state: CounterState) -> dict:
    return {
        "numbers": [1, 2, 3],   # 會「追加」到 numbers 列表
        "total": 6,              # 會「覆蓋」 total 的值
    }

def add_more_numbers(state: CounterState) -> dict:
    return {
        "numbers": [4, 5],      # 會繼續「追加」
        "total": 15,             # 會再次「覆蓋」
    }

graph_builder = StateGraph(CounterState)
graph_builder.add_node("first", add_numbers)
graph_builder.add_node("second", add_more_numbers)
graph_builder.add_edge(START, "first")
graph_builder.add_edge("first", "second")
graph_builder.add_edge("second", END)
graph = graph_builder.compile()

result = graph.invoke({"numbers": [], "total": 0})

print(result)
# {'numbers': [1, 2, 3, 4, 5], 'total': 15}
# numbers 被追加了，total 被覆蓋了
