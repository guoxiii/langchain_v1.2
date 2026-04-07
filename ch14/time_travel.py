# 檔案名稱：time_travel.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    value: str
    history: list[str]

def step_a(state: State) -> dict:
    new_value = f"{state['value']} → A"
    print(f"Step A: {new_value}")
    return {"value": new_value, "history": [*state.get("history", []), "step_a"]}

def step_b(state: State) -> dict:
    new_value = f"{state['value']} → B"
    print(f"Step B: {new_value}")
    return {"value": new_value, "history": [*state.get("history", []), "step_b"]}

def step_c(state: State) -> dict:
    new_value = f"{state['value']} → C"
    print(f"Step C: {new_value}")
    return {"value": new_value, "history": [*state.get("history", []), "step_c"]}

# 建立圖
graph = StateGraph(State)
graph.add_node("step_a", step_a)
graph.add_node("step_b", step_b)
graph.add_node("step_c", step_c)
graph.add_edge(START, "step_a")
graph.add_edge("step_a", "step_b")
graph.add_edge("step_b", "step_c")
graph.add_edge("step_c", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# 執行完整流程
config = {"configurable": {"thread_id": "time-travel-1"}}

result = app.invoke(
    {"value": "開始", "history": []},
    config=config
)

print(f"\n完成：{result['value']}")
print(f"歷史：{result['history']}")

# === 瀏覽所有 Checkpoint ===
print("\n" + "=" * 50)
print("📜 執行歷史：")

for i, snapshot in enumerate(app.get_state_history(config)):
    print(f"\n--- Checkpoint {i} ---")
    print(f"  值：{snapshot.values.get('value', '(初始)')}")
    print(f"  下一步：{snapshot.next}")
    print(f"  Config：{snapshot.config['configurable']}")
