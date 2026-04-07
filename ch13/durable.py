# 檔案名稱：durable.py

"""
Durable Execution 示範 — 中斷與恢復
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class ApprovalState(TypedDict):
    request: str
    approved: bool
    result: str

def prepare_request(state: ApprovalState) -> dict:
    """準備請求"""
    return {"request": f"處理中：{state['request']}"}

def execute_action(state: ApprovalState) -> dict:
    """執行動作（需要先通過審核）"""
    if state.get("approved"):
        return {"result": f"已執行：{state['request']}"}
    else:
        return {"result": "未通過審核，動作取消"}

# 建立圖
graph_builder = StateGraph(ApprovalState)
graph_builder.add_node("prepare", prepare_request)
graph_builder.add_node("execute", execute_action)
graph_builder.add_edge(START, "prepare")
graph_builder.add_edge("prepare", "execute")
graph_builder.add_edge("execute", END)

checkpointer = InMemorySaver()

# 在 execute 節點之前中斷！
graph = graph_builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute"],
)

config = {"configurable": {"thread_id": "approval-001"}}

# 第一次 invoke：會執行 prepare，然後在 execute 之前暫停
result = graph.invoke({"request": "刪除所有資料"}, config=config)
print("暫停中...")

# 查看目前狀態
state = graph.get_state(config)

print(f"目前狀態：{state.values}")
print(f"下一個節點：{state.next}")

# 模擬人工審核：更新狀態，加入 approved=True
graph.update_state(config, {"approved": True})

# 恢復執行：從中斷點繼續
result = graph.invoke(None, config=config)
print(f"最終結果：{result['result']}")
