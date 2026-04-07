"""
檔案：tests/test_agent_integration.py
Agent 整合測試（需要 API Key）
"""

import pytest

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool

@tool
def get_product_info(product_id: str) -> str:
    """查詢商品資訊"""
    products = {
        "P001": "iPhone 16 Pro, 價格 NT$38,900, 庫存: 50",
        "P002": "MacBook Air M4, 價格 NT$35,900, 庫存: 0",
    }

    return products.get(product_id, "商品不存在")

@pytest.fixture
def agent():
    return create_agent(
        model="google_genai:gemini-2.5-flash",
        tools=[get_product_info],
        system_prompt="你是電商客服，用繁體中文回答。",
    )

@pytest.mark.asyncio
async def test_agent_can_answer_product_query(agent):
    """測試 Agent 能正確回答商品查詢"""
    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "P001 的價格是多少？"}
        ],
    })

    # 取得最後一則 AI 訊息
    last_message = result["messages"][-1]
    response_text = last_message.content.lower()

    # 寬鬆斷言：只驗證關鍵資訊是否出現
    assert "38,900" in response_text or "38900" in response_text

@pytest.mark.asyncio
async def test_agent_handles_out_of_stock(agent):
    """測試 Agent 能正確處理缺貨情境"""
    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "P002 還有庫存嗎？"}
        ],
    })

    last_message = result["messages"][-1]
    response_text = last_message.content

    # 回答中應該提到缺貨或庫存為 0 的相關字眼
    stock_keywords = ["缺貨", "沒有庫存", "庫存: 0", "庫存為 0", "無庫存", "售完"]
    assert any(kw in response_text for kw in stock_keywords)

@pytest.mark.asyncio
async def test_agent_calls_correct_tool(agent):
    """測試 Agent 有呼叫正確的工具"""
    result = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "請查詢商品 P001 的資訊"}
        ],
    })

    # 檢查訊息歷史中是否有 tool 呼叫
    messages = result["messages"]
    tool_calls = [
        msg for msg in messages
        if hasattr(msg, "tool_calls") and msg.tool_calls
    ]

    assert len(tool_calls) > 0
    # 驗證呼叫了正確的工具
    called_tools = [
        tc["name"] for msg in tool_calls for tc in msg.tool_calls
    ]

    assert "get_product_info" in called_tools
