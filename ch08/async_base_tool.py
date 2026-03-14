# ch08/async_base_tool.py
from dotenv import load_dotenv

load_dotenv()

import httpx
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class MultiUrlInput(BaseModel):
    """多網址檢查的輸入。"""
    urls: list[str] = Field(description="要檢查的網址列表")

class UrlHealthChecker(BaseTool):
    """批次檢查多個網址的連線狀態。"""
    name: str = "check_urls"
    description: str = "批次檢查多個網址是否可以正常連線，回傳各網址的 HTTP 狀態碼。"
    args_schema: Type[BaseModel] = MultiUrlInput

    def _run(self, urls: list[str]) -> str:
        """同步版本（fallback）。"""
        import httpx as sync_httpx
        results = []

        for url in urls:
            try:
                resp = sync_httpx.get(url, timeout=5.0, follow_redirects=True)
                results.append(f"  {url} → {resp.status_code}")
            except Exception as e:
                results.append(f"  {url} → 錯誤: {e}")

        return "網址檢查結果：\n" + "\n".join(results)

    async def _arun(self, urls: list[str]) -> str:
        """非同步版本（推薦）— 所有 URL 同時發送請求。"""
        import asyncio

        async def check_one(client: httpx.AsyncClient, url: str) -> str:
            try:
                resp = await client.get(url, timeout=5.0, follow_redirects=True)
                return f"  {url} → {resp.status_code}"
            except Exception as e:
                return f"  {url} → 錯誤: {e}"

        async with httpx.AsyncClient() as client:
            tasks = [check_one(client, url) for url in urls]
            results = await asyncio.gather(*tasks)

        return "網址檢查結果：\n" + "\n".join(results)
