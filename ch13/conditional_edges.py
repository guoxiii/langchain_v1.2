# 檔案名稱：conditional_edges.py

"""
條件邊示範 — 根據分數決定通過或補考
"""

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class ExamState(TypedDict):
    student_name: str
    score: int
    result: str

def evaluate(state: ExamState) -> dict:
    """模擬評分（實際場景可能是 LLM 評估）"""
    # 這裡先直接用傳入的分數
    return {}

def pass_student(state: ExamState) -> dict:
    """通過的處理"""
    return {"result": f"恭喜 {state['student_name']}，考試通過！分數：{state['score']}"}

def fail_student(state: ExamState) -> dict:
    """未通過的處理"""
    return {"result": f"{state['student_name']} 需要補考，目前分數：{state['score']}"}

# 路由函式：決定走哪條路
def check_score(state: ExamState) -> Literal["pass", "fail"]:
    """根據分數決定通過或補考"""
    if state["score"] >= 60:
        return "pass"
    else:
        return "fail"

# 建立圖
graph_builder = StateGraph(ExamState)
graph_builder.add_node("evaluate", evaluate)
graph_builder.add_node("pass", pass_student)
graph_builder.add_node("fail", fail_student)
graph_builder.add_edge(START, "evaluate")

# 條件邊：evaluate 做完後，根據 check_score 的結果決定去 pass 還是 fail
graph_builder.add_conditional_edges(
    "evaluate",          # 來源節點
    check_score,         # 路由函式
    {                    # 路由映射
        "pass": "pass",
        "fail": "fail",
    }
)

graph_builder.add_edge("pass", END)
graph_builder.add_edge("fail", END)
graph = graph_builder.compile()

# 測試通過的情況， 恭喜小明，考試通過！分數：85
result1 = graph.invoke({"student_name": "小明", "score": 85})
print(result1["result"])
# 測試未通過的情況
result2 = graph.invoke({"student_name": "小華", "score": 45})

# 小華 需要補考，目前分數：45
print(result2["result"])
