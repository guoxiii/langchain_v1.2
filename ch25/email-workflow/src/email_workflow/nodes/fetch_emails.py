# src/email_workflow/nodes/fetch_emails.py

"""郵件擷取節點 — 從 Gmail MCP Server 抓取未讀郵件"""

from __future__ import annotations
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.email_workflow.state import WorkflowState, EmailItem
from src.email_workflow.tools.gmail_mcp import get_mcp_client_config

async def fetch_emails(state: WorkflowState) -> dict:
    """
    工作流第一站：從 Gmail 撈取未讀郵件

    這個節點做三件事：
    1. 透過 MCP 連接 Gmail（或模擬 Server）
    2. 用 Agent 搜尋並讀取未讀郵件
    3. 把郵件轉成 EmailItem 格式存入 state

    就像是收發室小妹每天早上第一件事：
    去信箱把所有新的信件抱回辦公室。
    """

    config = get_mcp_client_config()

    # langchain-mcp-adapters 0.1.0+ 不再支援 async with 用法
    client = MultiServerMCPClient(config)
    tools = await client.get_tools()

    # 建立一個專門抓郵件的 Agent
    model = init_chat_model("anthropic:claude-sonnet-4-6")

    fetch_agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "你是一個郵件擷取助手。請搜尋最近 24 小時內的未讀郵件，"
            "並以 JSON 陣列格式回傳每封郵件的以下資訊：\n"
            "- email_id: 郵件 ID\n"
            "- sender: 寄件人\n"
            "- subject: 主旨\n"
            "- body: 內文前 500 字\n"
            "- received_at: 收件時間\n\n"
            "請先使用 gmail_search 工具搜尋 'is:unread newer_than:1d'，"
            "然後用 gmail_read 工具逐一讀取每封郵件的完整內容，"
            "最後把所有郵件整理成 JSON 陣列回覆給我。"
        ),
    )

    # 執行 Agent 抓取郵件
    result = await fetch_agent.ainvoke({
        "messages": [
            {"role": "user", "content": "請搜尋並讀取最近 24 小時的未讀郵件"}
        ]
    })

    # 解析 Agent 回傳的郵件資料
    emails = _parse_email_response(result)

    return {
        "emails": emails,
        "workflow_status": "classifying",
        "stats": {**state.stats, "total": len(emails)},
    }

def _parse_email_response(result: dict) -> list[EmailItem]:
    """
    解析 Agent 回傳結果，轉換成 EmailItem 列表
    Agent 回傳的格式不一定完美，所以我們需要做一些容錯處理。
    """
    emails = []

    last_message = result["messages"][-1]

    try:
        content = last_message.content

        # Gemini 模型的 content 可能是 list（多個 content block）而非 str
        if isinstance(content, list):
            content = "\n".join(
                block if isinstance(block, str)
                else block.get("text", "")
                for block in content
            )

        # 找到 JSON 陣列的起止位置
        start = content.find("[")
        end = content.rfind("]") + 1

        if start != -1 and end > start:
            raw_emails = json.loads(content[start:end])
            for raw in raw_emails:
                emails.append(EmailItem(
                    email_id=raw.get("email_id", f"unknown-{len(emails)}"),
                    sender=raw.get("sender", "unknown"),
                    subject=raw.get("subject", "（無主旨）"),
                    body=raw.get("body", "")[:500],
                    received_at=raw.get(
                        "received_at",
                        datetime.now().isoformat()
                    ),
                ))
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # 解析失敗時記錄錯誤，但不中斷流程
        print(f"⚠️ 郵件解析錯誤：{e}")

    return emails