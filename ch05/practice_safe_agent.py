# 檔案：ch05/practice_safe_agent.py

"""
第五章實作練習：安全客服 Agent
結合 PIIMiddleware + SummarizationMiddleware +
HumanInTheLoopMiddleware + ModelRetryMiddleware
"""

import os
import re
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    PIIMiddleware,
    SummarizationMiddleware,
    HumanInTheLoopMiddleware,
    ModelRetryMiddleware,
)

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()

# ===========================
# 第一部分：定義工具
# ===========================

@tool
def lookup_order(order_id: str) -> str:
    """根據訂單編號查詢訂單狀態"""
    # 模擬訂單資料庫
    orders = {
        "ORD-001": {"status": "已出貨", "item": "藍牙耳機", "amount": 1290},
        "ORD-002": {"status": "處理中", "item": "USB-C 充電線", "amount": 350},
        "ORD-003": {"status": "已送達", "item": "無線滑鼠", "amount": 890},
    }

    order = orders.get(order_id)
    if order:
        return (
            f"訂單 {order_id}：\n"
            f"  商品：{order['item']}\n"
            f"  金額：NT${order['amount']}\n"
            f"  狀態：{order['status']}"
        )

    return f"找不到訂單 {order_id}"

@tool
def process_refund(order_id: str, reason: str) -> str:
    """處理退款申請（需要人工審核）"""
    return f"退款申請已提交：訂單 {order_id}，原因：{reason}"

@tool
def send_notification(customer_name: str, message: str) -> str:
    """發送通知給客戶（需要人工審核）"""
    return f"通知已發送給 {customer_name}：{message}"

# ===========================
# 第二部分：設定 Middleware
# ===========================

middlewares = [
    # --- 第一層：PII 遮蔽 ---
    PIIMiddleware("email", strategy="redact", apply_to_input=True),
    PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),

    PIIMiddleware(
        "phone_tw",
        detector=r"09\d{2}-?\d{3}-?\d{3}",
        strategy="redact",
        apply_to_input=True,
    ),

    # --- 第二層：對話摘要 ---
    SummarizationMiddleware(
        model="google_genai:gemini-2.5-flash",
        trigger=("messages", 20),
        keep=("messages", 10),
    ),

    # --- 第三層：模型重試 ---
    ModelRetryMiddleware(
        max_retries=2,
        backoff_factor=2.0,
        initial_delay=1.0,
    ),

    # --- 第四層：人工審核 ---
    HumanInTheLoopMiddleware(
        interrupt_on={
            "process_refund": {
                "allowed_decisions": ["approve", "edit", "reject"],
                "description": "退款操作需要主管審核",
            },
            "send_notification": {
                "allowed_decisions": ["approve", "reject"],
                "description": "客戶通知需要確認後才能發送",
            },
            "lookup_order": False,  # 查詢不需要審核
        }
    ),
]

# ===========================
# 第三部分：建立 Agent
# ===========================

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[lookup_order, process_refund, send_notification],
    middleware=middlewares,
    checkpointer=InMemorySaver(),
    system_prompt=(
        "你是一位專業的客服助理。\n"
        "你可以查詢訂單狀態、處理退款、發送通知。\n"
        "回覆時請使用繁體中文，語氣要親切有禮。"
    ),
)

# ===========================
# 第四部分：輔助函式
# ===========================

def handle_interrupt(result, thread_config, decision_type="approve"):
    """
    處理 HumanInTheLoopMiddleware 的 interrupt。
    若 result 中有 __interrupt__，就對所有待審核動作
    統一回覆 decision_type（預設 approve），並回傳恢復後的 result。
    若沒有 interrupt，則原封不動回傳。
    """
    while result.get("__interrupt__"):
        intr_value = result["__interrupt__"][0].value
        action_requests = intr_value["action_requests"]

        # 印出所有待審核操作
        for req in action_requests:
            print(f"   📋 待審核：{req['name']}（{req['description']}）")
            print(f"      參數：{req['args']}")

        print(f"\n   ✅ 審核決定：全部 {decision_type}")

        # 針對每個 action_request 各給一個 decision
        decisions = [{"type": decision_type} for _ in action_requests]

        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=thread_config,
        )

    return result


# ===========================
# 第五部分：模擬客服對話
# ===========================

def run_customer_service():
    """模擬客服對話流程"""
    thread_config = {"configurable": {"thread_id": "cs-session-001"}}

    print("=" * 60)
    print("🎧 安全客服 Agent 啟動")
    print("=" * 60)

    # --- 對話 1：查詢訂單（lookup_order 不需審核） ---
    print("\n--- 對話 1：查詢訂單 ---")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "我要查詢訂單 ORD-001 的狀態"}]},
        config=thread_config,
    )
    # 即使 lookup_order 設定 False，養成每次都檢查的好習慣
    result = handle_interrupt(result, thread_config)
    print(f"🤖 {result['messages'][-1].content}")

    # --- 對話 2：包含 PII 的訊息 ---
    # ⚠️ 模型可能會同時產生文字回覆和 tool_use（例如直接嘗試退款），
    #    此時 HumanInTheLoopMiddleware 會觸發 interrupt，必須處理！
    print("\n--- 對話 2：包含 PII 的訊息 ---")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "我的 Email 是 alice@example.com，手機是 0912-345-678，商品有問題想退款"}]},
        config=thread_config,
    )

    if result.get("__interrupt__"):
        print("⏸️ 對話 2 觸發了人工審核（模型主動嘗試呼叫工具）")
        result = handle_interrupt(result, thread_config)

    print(f"🤖 {result['messages'][-1].content}")

    # --- 對話 3：觸發退款（需要人工審核） ---
    print("\n--- 對話 3：請求退款 ---")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "請幫我處理 ORD-001 的退款，原因是商品有瑕疵"}]},
        config=thread_config,
    )

    if result.get("__interrupt__"):
        print("⏸️ Agent 已暫停，等待人工審核...")
        result = handle_interrupt(result, thread_config)

    print(f"🤖 {result['messages'][-1].content}")

    print("\n" + "=" * 60)
    print("🎧 客服對話結束")
    print("=" * 60)

# 執行
if __name__ == "__main__":
    run_customer_service()