# 檔案名稱：command_in_node.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

class State(TypedDict):
    task: str
    priority: str
    result: str

def triage_node(state: State) -> Command[Literal["urgent_handler", "normal_handler"]]:
    """根據優先級決定走哪條路，直接用 Command 控制路由"""
    priority = state.get("priority", "normal")    

    if priority == "high":
        # 用 Command 跳到 urgent_handler，同時更新狀態
        return Command(
            goto="urgent_handler",
            update={"result": "轉交緊急處理通道"}
        )
    else:
        return Command(
            goto="normal_handler",
            update={"result": "進入一般處理通道"}
        )

def urgent_handler(state: State) -> dict:
    print(f"🔴 緊急處理：{state['task']}")
    return {"result": f"已緊急完成：{state['task']}"}

def normal_handler(state: State) -> dict:
    print(f"🟢 一般處理：{state['task']}")
    return {"result": f"已完成：{state['task']}"}

# 建立圖
graph = StateGraph(State)
graph.add_node("triage", triage_node)
graph.add_node("urgent_handler", urgent_handler)
graph.add_node("normal_handler", normal_handler)
graph.add_edge(START, "triage")

# 注意：因為 triage_node 回傳 Command，所以不需要手動加邊到 urgent/normal
# Command 的 goto 會自動處理路由
graph.add_edge("urgent_handler", END)
graph.add_edge("normal_handler", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# 測試
config = {"configurable": {"thread_id": "triage-1"}}

result = app.invoke(
    {"task": "伺服器當機", "priority": "high", "result": ""},
    config=config
)

print(f"結果：{result['result']}")
