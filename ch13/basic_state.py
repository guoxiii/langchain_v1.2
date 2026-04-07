# 檔案名稱：basic_state.py

"""
第一個 LangGraph 範例 — 理解 State 的基本運作
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# 第一步：定義 State
class GreetingState(TypedDict):
    name: str
    greeting: str

# 第二步：定義 Node（就是普通的 Python 函式）
def create_greeting(state: GreetingState) -> dict:
    """接收名字，產生問候語"""
    name = state["name"]
    return {"greeting": f"你好，{name}！歡迎來到 LangGraph 的世界！"}

# 第三步：建立圖
graph_builder = StateGraph(GreetingState)

# 第四步：加入節點
graph_builder.add_node("greeter", create_greeting)

# 第五步：定義邊 — 從起點到 greeter，再從 greeter 到終點
graph_builder.add_edge(START, "greeter")
graph_builder.add_edge("greeter", END)

# 第六步：編譯圖
graph = graph_builder.compile()

# 第七步：執行！
result = graph.invoke({"name": "小明"})
print(result)

# 輸出：{'name': '小明', 'greeting': '你好，小明！歡迎來到 LangGraph 的世界！'}
