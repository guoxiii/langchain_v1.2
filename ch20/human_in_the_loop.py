# human_in_the_loop.py

"""
HumanInTheLoopMiddleware：高風險操作的人工審核
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# === 定義工具 ===

@tool
def transfer_money(amount: float, to_account: str) -> str:
    """轉帳到指定帳戶。"""
    return f"已成功轉帳 ${amount:,.2f} 至帳戶 {to_account}"

@tool
def check_balance() -> str:
    """查詢帳戶餘額。"""
    return "目前帳戶餘額:$50,000.00"

@tool
def get_exchange_rate(currency: str) -> str:
    """查詢匯率。"""
    rates = {"USD": 31.5, "JPY": 0.21, "EUR": 34.2}
    rate = rates.get(currency.upper(), None)

    if rate:
        return f"1 {currency.upper()} = {rate} TWD"
    return f"找不到 {currency} 的匯率資訊"

# === 建立 Agent(帶人工審核) ===
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[transfer_money, check_balance, get_exchange_rate],
    middleware=[
        # 只有 transfer_money 需要人工審核
        # check_balance 和 get_exchange_rate 是安全操作,不需要審核
        HumanInTheLoopMiddleware(
            interrupt_on={"transfer_money": True}
        ),
    ],

    # HITL 需要 Checkpointer 來保存中斷狀態
    checkpointer=MemorySaver(),
)

# === 使用方式 ===

# 步驟 1:發起請求
config = {"configurable": {"thread_id": "transfer-001"}}

result = agent.invoke(
    {
        "messages": [{
            "role": "user",
            "content": "請幫我轉帳 $1,000 到帳戶 ACC-98765"
        }]
    },
    config=config,
)

# 此時 Agent 會暫停在 transfer_money 工具呼叫之前
print("⏸️ Agent 暫停,等待人工審核...")
print(f"待審核的操作:transfer_money")
print(f"參數:amount=1000, to_account=ACC-98765")
print()

# 步驟 2:人工審核(在實際應用中,這會是一個 UI 介面)

# 選項 A:批准執行
approved_result = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
)
print("✅ 審核通過,執行結果:")
print(approved_result["messages"][-1].text)

# 選項 B:拒絕執行(注意:欄位名稱為 message,而非 reason)
"""
rejected_result = agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "message": "金額超出日限額"}]}),
    config=config,
)

print("✅ 拒絕執行,執行結果:")
print(rejected_result["messages"][-1].text)
"""