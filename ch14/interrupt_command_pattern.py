# 檔案名稱：interrupt_command_pattern.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class OrderState(TypedDict):
    item: str
    quantity: int
    total_price: float
    confirmed: bool

def calculate_price(state: OrderState) -> dict:
    # 假設每個商品 100 元
    total = state["quantity"] * 100.0
    print(f"💰 計算價格：{state['item']} x {state['quantity']} = ${total}")
    return {"total_price": total}

def confirm_order(state: OrderState) -> dict:
    """讓人類確認訂單"""
    # interrupt 暫停，顯示訂單摘要給人類
    decision = interrupt({
        "message": "請確認訂單",
        "item": state["item"],
        "quantity": state["quantity"],
        "total_price": state["total_price"],
        "instruction": "回覆 True 確認，False 取消"
    })    

    return {"confirmed": decision}

def process_order(state: OrderState) -> dict:
    if state["confirmed"]:
        print(f"📦 訂單已處理：{state['item']} x {state['quantity']}")
        return {"item": f"[已出貨] {state['item']}"}
    else:
        print(f"🚫 訂單已取消")
        return {"item": f"[已取消] {state['item']}"}

# 建立圖
graph = StateGraph(OrderState)
graph.add_node("calculate_price", calculate_price)
graph.add_node("confirm_order", confirm_order)
graph.add_node("process_order", process_order)
graph.add_edge(START, "calculate_price")
graph.add_edge("calculate_price", "confirm_order")
graph.add_edge("confirm_order", "process_order")
graph.add_edge("process_order", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# --- 執行 ---
config = {"configurable": {"thread_id": "order-1"}}

# 第一步：啟動，會在 confirm_order 暫停
result = app.invoke(
    {"item": "機械鍵盤", "quantity": 2, "total_price": 0.0, "confirmed": False},
    config=config
)

print(f"⏸️  訂單等待確認...")

# 第二步：人類確認
result = app.invoke(
    Command(resume=True),  # 確認訂單
    config=config
)

print(f"最終結果：{result}")
