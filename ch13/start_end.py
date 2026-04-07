# 檔案名稱：start_end.py

"""
展示 START 和 END 的多種用法
"""

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class TaskState(TypedDict):
    task_type: str
    content: str
    result: str

def handle_email(state: TaskState) -> dict:
    return {"result": f"已處理電子郵件：{state['content']}"}

def handle_ticket(state: TaskState) -> dict:
    return {"result": f"已建立工單：{state['content']}"}

def handle_unknown(state: TaskState) -> dict:
    return {"result": f"無法辨識的任務類型：{state['task_type']}"}

# 路由函式
def route_task(state: TaskState) -> Literal["email", "ticket", "unknown"]:
    task_type = state["task_type"]
    if task_type == "email":
        return "email"
    elif task_type == "ticket":
        return "ticket"
    else:
        return "unknown"

# 建立圖
graph_builder = StateGraph(TaskState)
graph_builder.add_node("email", handle_email)
graph_builder.add_node("ticket", handle_ticket)
graph_builder.add_node("unknown", handle_unknown)

# START 使用條件邊
graph_builder.add_conditional_edges(
    START,
    route_task,
    {
        "email": "email",
        "ticket": "ticket",
        "unknown": "unknown",
    }
)

# 三個節點都通往 END（多出口）
graph_builder.add_edge("email", END)
graph_builder.add_edge("ticket", END)
graph_builder.add_edge("unknown", END)
graph = graph_builder.compile()

# 測試
print(graph.invoke({"task_type": "email", "content": "會議通知"})["result"])

# 已處理電子郵件：會議通知
print(graph.invoke({"task_type": "ticket", "content": "伺服器異常"})["result"])

# 已建立工單：伺服器異常
