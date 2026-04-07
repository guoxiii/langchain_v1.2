from typing import Annotated
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

def extract_text(content) -> str:
    """將 LLM 回傳的 content 正規化為純文字。

    Gemini 2.5 等模型在啟用 thinking 時會回傳 list[dict] 格式的
    content blocks,需要把 type='text' 的區塊抽出來合併。
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)

# === 定義擴展的 State ===
class TeamState(AgentState):
    """擴展 AgentState,加入團隊共享的結構化資料。"""
    research_data: dict       # 研究資料
    article_draft: str        # 文章草稿
    review_status: str        # 審核狀態

# === 子 Agent 用 Command 回傳結構化結果 ===
research_agent = create_agent(
    model,
    tools=[],
    system_prompt="你是研究員。請根據主題進行研究並回覆研究結果。",
    name="researcher",
    state_schema=TeamState,
)

@tool("do_research", description="進行主題研究")
def do_research(
    topic: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """研究指定主題,回傳研究數據。"""
    result = research_agent.invoke(
        {"messages": [{"role": "user", "content": f"請研究:{topic}"}]}
    )

    # 將 content blocks 正規化為純文字,方便後續寫入 State
    research_content = extract_text(result["messages"][-1].content)

    # 透過 Command 更新結構化 State
    return Command(update={
        "research_data": {
            "topic": topic,
            "findings": research_content,
            "source_count": 5,
        },
        "messages": [
            ToolMessage(
                content=research_content,
                tool_call_id=tool_call_id,
            )
        ],
    })

# Supervisor 可以讀取 State 中的結構化資料
supervisor = create_agent(
    model,
    tools=[do_research],
    system_prompt="你是專案經理。使用工具進行研究,然後基於研究結果回覆使用者。",
    name="supervisor",
    state_schema=TeamState,
)

def main():
    result = supervisor.invoke({
        "messages": [{"role": "user", "content": "請研究 AI 在教育領域的應用"}],
        "research_data": {},
        "article_draft": "",
        "review_status": "pending",
    })

    final_content = extract_text(result["messages"][-1].content)
    print("最終回覆:", final_content)
    print("研究資料:", result.get("research_data", {}))

if __name__ == "__main__":
    main()