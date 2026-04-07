# ch08/async_tool.py
from dotenv import load_dotenv

load_dotenv()

import asyncio
import httpx
from langchain.tools import tool

@tool
async def fetch_webpage_title(url: str) -> str:
    """擷取指定網頁的標題。

    Args:
        url: 網頁的完整 URL（需包含 https://）
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            html = response.text
            # 簡易解析 <title> 標籤
            start = html.find("<title>")
            end = html.find("</title>")

            if start != -1 and end != -1:
                title = html[start + 7:end].strip()
                return f"網頁標題：{title}"

            return "找不到網頁標題"
    except Exception as e:
        return f"擷取失敗：{e}"

# 非同步工具需要在 async 環境中呼叫
async def main():
    result = await fetch_webpage_title.ainvoke({"url": "https://www.python.org"})
    print(result)

asyncio.run(main())
