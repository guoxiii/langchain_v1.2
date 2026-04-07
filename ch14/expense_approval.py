# 檔案名稱：expense_approval.py

from dotenv import load_dotenv
load_dotenv()

import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command, Send
from langchain.chat_models import init_chat_model

# 初始化模型
llm = init_chat_model("google_genai:gemini-2.5-flash")

# === 狀態定義 ===
class ExpenseState(TypedDict):
    # 申請資訊
    employee: str
    description: str
    amount: float
    category: str    

    # 處理過程
    compliance_check: str
    risk_analyses: Annotated[list[str], operator.add]    

    # 審批結果
    decision: str  # "approved", "rejected", "auto_approved"
    reason: str
    final_status: str

# Map-Reduce 工人的狀態
class RiskWorkerState(TypedDict):
    description: str
    amount: float
    perspective: str  # 分析角度
    risk_analyses: Annotated[list[str], operator.add]

# === 節點定義 ===
def submit_expense(state: ExpenseState) -> dict:
    """節點 1：接收並記錄報銷申請"""
    print(f"📝 收到報銷申請：")
    print(f"   員工：{state['employee']}")
    print(f"   說明：{state['description']}")
    print(f"   金額：${state['amount']:,.0f}")
    print(f"   類別：{state['category']}")
    return {}

def compliance_check(state: ExpenseState) -> dict:
    """節點 2：AI 合規檢查"""
    response = llm.invoke(
        f"你是一位財務合規專員。請檢查以下報銷申請的內容是否屬於合理的業務支出：\n"
        f"- 說明：{state['description']}\n"
        f"- 金額：${state['amount']:,.0f}\n"
        f"- 類別：{state['category']}\n\n"
        f"注意：所有必要的發票、收據及佐證文件均已附上，無須考慮文件是否齊全。\n"
        f"你只需要判斷這筆支出的用途是否屬於正當的業務開支。\n"
        f"只有明顯不合理的申請（如私人消費冒充公務）才應判定不通過。\n"
        f"回覆格式：[通過/不通過] 原因（一句話）"
    )

    result = response.content.strip()
    print(f"🔍 合規檢查：{result}")

    return {"compliance_check": result}

def auto_approve(state: ExpenseState) -> dict:
    """節點 3a：自動核准（小額）"""
    print(f"✅ 自動核准：${state['amount']:,.0f}（小額免審）")

    return {
        "decision": "auto_approved",
        "reason": "金額低於 $1,000，自動核准",
        "final_status": "已核准"
    }

def auto_reject(state: ExpenseState) -> dict:
    """節點 3b：自動拒絕（合規不通過）"""
    print(f"❌ 自動拒絕：合規檢查未通過")
    return {
        "decision": "rejected",
        "reason": f"合規檢查未通過：{state['compliance_check']}",
        "final_status": "已拒絕"
    }

# --- Map-Reduce：風險分析 ---
def analyze_risk(state: RiskWorkerState) -> dict:
    """Map 工人：從特定角度分析風險"""
    response = llm.invoke(
        f"你是一位{state['perspective']}專家。\n"
        f"請從{state['perspective']}的角度，用 1-2 句話評估以下報銷申請的風險：\n"
        f"- 說明：{state['description']}\n"
        f"- 金額：${state['amount']:,.0f}\n"
        f"回覆格式：[風險等級：高/中/低] 分析說明"
    )

    result = f"【{state['perspective']}】{response.content.strip()}"
    print(f"🔬 {result}")

    return {"risk_analyses": [result]}

# --- 主管審核（Human-in-the-Loop）---
def manager_review(state: ExpenseState) -> dict:
    """節點 4：主管審核（使用 interrupt）"""
    risk_info = ""

    if state.get("risk_analyses"):
        risk_info = "\n\n📊 風險分析報告：\n" + "\n".join(state["risk_analyses"])    

    # 觸發 interrupt，等待主管審核
    decision = interrupt({
        "message": "📋 費用報銷審核",
        "employee": state["employee"],
        "description": state["description"],
        "amount": state["amount"],
        "category": state["category"],
        "compliance": state["compliance_check"],
        "risk_analysis": risk_info if risk_info else "（無風險分析）",
        "instruction": "請回覆：{'decision': 'approve/reject', 'reason': '原因'}"
    })    

    return {
        "decision": decision.get("decision", "rejected"),
        "reason": decision.get("reason", ""),
    }

def finalize(state: ExpenseState) -> dict:
    """節點 5：最終處理"""
    if state["decision"] in ["approved", "approve", "auto_approved"]:
        status = f"✅ 已核准 — ${state['amount']:,.0f} 將撥付給 {state['employee']}"
        final = "已核准"
    else:
        status = f"❌ 已拒絕 — 原因：{state['reason']}"
        final = "已拒絕"    

    print(f"\n{'=' * 50}")
    print(f"📋 最終結果：{status}")

    return {"final_status": final}

# === 建立圖結構 ===
graph = StateGraph(ExpenseState)
graph.add_node("submit", submit_expense)
graph.add_node("compliance", compliance_check)
graph.add_node("auto_approve", auto_approve)
graph.add_node("auto_reject", auto_reject)
graph.add_node("analyze_risk", analyze_risk)
graph.add_node("manager_review", manager_review)
graph.add_node("finalize", finalize)
graph.add_edge(START, "submit")
graph.add_edge("submit", "compliance")

# 合規後路由
def route_after_compliance(state: ExpenseState) -> str | list[Send]:
    """根據合規結果和金額決定下一步"""
    if "不通過" in state["compliance_check"]:
        return "auto_reject"
    elif state["amount"] <= 1000:
        return "auto_approve"
    elif state["amount"] > 5000:
        # 大額：使用 Send 做並行風險分析
        perspectives = ["財務風險", "合規風險", "營運必要性"]

        return [
            Send(
                "analyze_risk",
                {
                    "description": state["description"],
                    "amount": state["amount"],
                    "perspective": p,
                    "risk_analyses": []
                }
            )
            for p in perspectives
        ]
    else:
        return "manager_review"

graph.add_conditional_edges(
    "compliance",
    route_after_compliance,
    ["auto_approve", "auto_reject", "analyze_risk", "manager_review"]
)

graph.add_edge("analyze_risk", "manager_review")
graph.add_edge("manager_review", "finalize")
graph.add_edge("auto_approve", "finalize")
graph.add_edge("auto_reject", "finalize")
graph.add_edge("finalize", END)

# 編譯
checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# === 測試場景 ===
# --- 場景 1：小額報銷（自動核准）---
print("🧪 場景 1：小額報銷")
print("=" * 50)

config1 = {"configurable": {"thread_id": "expense-1"}}

result = app.invoke(
    {
        "employee": "Alice",
        "description": "購買辦公室文具",
        "amount": 500.0,
        "category": "辦公用品",
        "compliance_check": "",
        "risk_analyses": [],
        "decision": "",
        "reason": "",
        "final_status": ""
    },
    config=config1
)

print(f"狀態：{result['final_status']}\n")

# --- 場景 2：大額報銷（需要風險分析 + 主管審核）---
print("🧪 場景 2：大額報銷")
print("=" * 50)

config2 = {"configurable": {"thread_id": "expense-2"}}

result = app.invoke(
    {
        "employee": "Bob",
        "description": "購買 Coursera 企業版年度授權（50 人），供工程團隊進修 AI 與雲端課程",
        "amount": 15000.0,
        "category": "教育訓練",
        "compliance_check": "",
        "risk_analyses": [],
        "decision": "",
        "reason": "",
        "final_status": ""
    },
    config=config2
)

print(f"\n⏸️  等待主管審核...")

# 主管審核
print("\n👤 主管決定核准...")

result = app.invoke(
    Command(resume={"decision": "approve", "reason": "培訓對團隊成長有幫助"}),
    config=config2
)

print(f"最終狀態：{result['final_status']}")