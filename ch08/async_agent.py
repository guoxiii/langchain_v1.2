# ch08/async_agent.py
from dotenv import load_dotenv

load_dotenv()

import asyncio
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

@tool
async def async_search(query: str) -> str:
    """非同步搜尋工具。

    Args:
        query: 搜尋關鍵字
    """

    # 模擬非同步搜尋
    await asyncio.sleep(0.5)  # 模擬網路延遲
    return f"搜尋「{query}」的結果：找到 42 筆相關資料"

@tool
async def async_translate(text: str, target_lang: str = "en") -> str:
    """非同步翻譯工具。

    Args:
        text: 要翻譯的文字
        target_lang: 目標語言代碼（例如 en、ja、ko）
    """

    await asyncio.sleep(0.3)  # 模擬 API 延遲
    return f"將「{text}」翻譯為 {target_lang}：[翻譯結果]"

async def main():
    model = init_chat_model("anthropic:claude-sonnet-4-6")
    agent = create_agent(
        model,
        tools=[async_search, async_translate],
        system_prompt="你是一個多功能助手，可以搜尋資料和翻譯文字。請用繁體中文回答。"
    )

    # 使用 ainvoke 進行非同步呼叫
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "幫我搜尋 LangChain 的最新版本，然後把結果翻譯成日文"}]}
    )

    for msg in result["messages"]:
        print(f"[{msg.type}] {msg.content}")

asyncio.run(main())
