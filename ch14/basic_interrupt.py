# 檔案名稱：basic_interrupt.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

# 定義狀態
class State(TypedDict):
    task: str
    approved: bool
    result: str

# 節點：產生計畫
def generate_plan(state: State) -> dict:
    task = state["task"]
    plan = f"計畫：將針對「{task}」執行以下步驟：1.分析需求 2.執行任務 3.產生報告"
    print(f"📋 已產生計畫：{plan}")
    return {"result": plan}

# 節點：人工審核（使用 interrupt）
def human_review(state: State) -> dict:
    # interrupt() 會暫停圖的執行
    # 傳入的值會作為「提示訊息」，告訴人類需要做什麼
    decision = interrupt(
        f"請審核以下計畫：\n{state['result']}\n\n請回覆 'approve' 或 'reject'"
    )    

    if decision == "approve":
        print("✅ 人工審核通過！")
        return {"approved": True}
    else:
        print("❌ 人工審核拒絕！")
        return {"approved": False}

# 節點：執行計畫
def execute_plan(state: State) -> dict:
    if state.get("approved"):
        return {"result": f"✅ 任務已完成：{state['task']}"}
    else:
        return {"result": f"🚫 任務已取消：{state['task']}"}

# 建立圖
graph = StateGraph(State)
graph.add_node("generate_plan", generate_plan)
graph.add_node("human_review", human_review)
graph.add_node("execute_plan", execute_plan)
graph.add_edge(START, "generate_plan")
graph.add_edge("generate_plan", "human_review")
graph.add_edge("human_review", "execute_plan")
graph.add_edge("execute_plan", END)

# 編譯時必須提供 checkpointer（中斷需要持久化狀態）
checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# --- 執行 ---
config = {"configurable": {"thread_id": "review-thread-1"}}

# 第一次呼叫：會執行到 interrupt 就暫停
print("🚀 第一次呼叫...")

result = app.invoke(
    {"task": "寄送月報給全體員工", "approved": False, "result": ""},
    config=config
)

print(f"第一次呼叫結果：{result}")
# 此時圖暫停在 human_review 節點
