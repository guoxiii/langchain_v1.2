# 檔案：ch05/hitl_basic.py

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# --- 定義工具 ---
@tool
def read_email(email_id: str) -> str:
    """讀取指定 ID 的 Email 內容"""
    return f"Email #{email_id} 的內容：明天下午三點開會。"

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """發送 Email 給指定收件人"""
    return f"Email 已發送給 {recipient}，主旨：{subject}"

# --- 建立 Agent ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[read_email, send_email],
    checkpointer=InMemorySaver(),  # ⚠️ HITL 必須搭配 Checkpointer
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    "description": "發送 Email 前需要人工審核",
                },
                "read_email": False,  # 讀取 Email 不需要審核
            }
        ),
    ],
)

# --- 執行 ---
thread_config = {"configurable": {"thread_id": "demo-001"}}

# 第一步：使用者提出請求
result = agent.invoke(
    {"messages": [{"role": "user", "content": "幫我寄一封 Email 給 boss@company.com，主旨是「請假申請」，內容是我明天要請假"}]},
    config=thread_config,
)

# 透過 get_state 檢查是否被中斷
state = agent.get_state(thread_config)
if state.next:
    print("⏸️ Agent 已暫停，等待人工審核...")
    last_msg = state.values["messages"][-1]
    for tc in last_msg.tool_calls:
        print(f"\n待審核的操作：{tc['name']}")
        print("參數：")
        for key, value in tc["args"].items():
            print(f"  {key}：{value}")
else:
    last_msg = state.values["messages"][-1]
    print(f"Agent 回覆：{last_msg.content}")