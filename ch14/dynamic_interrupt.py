# 檔案名稱：dynamic_interrupt.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class PaymentState(TypedDict):
    payee: str
    amount: float
    approved: bool
    result: str

def review_payment(state: PaymentState) -> dict:
    amount = state["amount"]
    payee = state["payee"]    

    # 動態判斷：只有金額超過 10000 或收款人是特殊對象時才需要人工審核
    needs_approval = amount > 10000 or payee in ["外部廠商", "海外帳戶"]    

    if needs_approval:
        # 需要人工審核——觸發 interrupt
        decision = interrupt({
            "message": f"⚠️ 高風險付款需要審核",
            "payee": payee,
            "amount": amount,
            "reason": "金額超過 $10,000" if amount > 10000 else f"特殊收款人：{payee}",
            "instruction": "回覆 True 核准，False 拒絕"
        })

        return {"approved": decision}
    else:
        # 不需要人工審核——自動核准
        print(f"✅ 自動核准：${amount} → {payee}")
        return {"approved": True}

def execute_payment(state: PaymentState) -> dict:
    if state["approved"]:
        result = f"💸 已付款 ${state['amount']} 給 {state['payee']}"
    else:
        result = f"🚫 付款已拒絕：${state['amount']} → {state['payee']}"

    print(result)
    return {"result": result}

# 建立圖
graph = StateGraph(PaymentState)
graph.add_node("review", review_payment)
graph.add_node("execute", execute_payment)
graph.add_edge(START, "review")
graph.add_edge("review", "execute")
graph.add_edge("execute", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# --- 測試 1：小額付款（自動核准，不會暫停）---
print("=" * 50)
print("測試 1：小額付款")
config1 = {"configurable": {"thread_id": "payment-1"}}

result = app.invoke(
    {"payee": "文具行", "amount": 500.0, "approved": False, "result": ""},
    config=config1
)

print(f"結果：{result['result']}")
# 不會暫停，直接完成

# --- 測試 2：大額付款（需要人工審核）---
print("\n" + "=" * 50)
print("測試 2：大額付款")
config2 = {"configurable": {"thread_id": "payment-2"}}

result = app.invoke(
    {"payee": "外部廠商", "amount": 50000.0, "approved": False, "result": ""},
    config=config2
)

print(f"⏸️  等待人工審核...")

# 人類核准
result = app.invoke(
    Command(resume=True),
    config=config2
)

print(f"結果：{result['result']}")
