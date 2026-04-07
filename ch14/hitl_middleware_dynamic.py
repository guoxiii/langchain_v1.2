# 檔案名稱：hitl_middleware_dynamic.py

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.tools import tool

@tool
def read_file(filename: str) -> str:
    """讀取檔案內容"""
    return f"檔案 {filename} 的內容：Hello World"

@tool
def delete_file(filename: str) -> str:
    """刪除檔案（危險操作）"""
    return f"檔案 {filename} 已刪除"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """寄送電子郵件"""
    return f"郵件已寄送給 {to}，主題：{subject}"

# 建立 Agent，配置 HITL Middleware
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[read_file, delete_file, send_email],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "read_file": False,        # 讀取檔案：自動允許，不需審核
                "delete_file": True,        # 刪除檔案：需要審核（所有決策都允許）
                "send_email": {             # 寄信：需要審核，但只能核准或拒絕（不能編輯）
                    "allowed_decisions": ["approve", "reject"]
                },
            },
            description_prefix="需要人工審核",
        ),
    ],
    checkpointer=InMemorySaver(),
)

# 使用
config = {"configurable": {"thread_id": "agent-1"}}

# 讓 Agent 執行任務
result = agent.invoke(
    {"messages": [{"role": "user", "content": "請刪除 temp.txt 這個檔案"}]},
    config=config
)

# 如果有中斷，result 會包含 __interrupt__ 資訊
# 人類審核後恢復
result = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config
)
