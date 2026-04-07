# src/document_processing/summarizer.py
"""AI 自動摘要產生器 — 你的 AI 速讀員"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from src.config import config

class DocumentSummarizer:
    """
    使用 LLM 為文件產生摘要

    策略：
    - 短文件（< 3000 字）：直接摘要
    - 長文件（>= 3000 字）：Map-Reduce 策略
      1. Map：為每個 chunk 產生小摘要
      2. Reduce：將所有小摘要合併為最終摘要
    """

    def __init__(self, model_name: str = config.primary_model):
        self.llm = init_chat_model(model_name, temperature=0)

    async def summarize(
        self, documents: list[Document], max_length: int = 300
    ) -> str:
        """
        為一組 Documents 產生摘要
        Parameters
        ----------
        documents : list[Document]
            切割後的 Document 列表（來自同一份檔案）

        max_length : int
            摘要的最大字數

        Returns
        -------

        str
            文件摘要
        """

        # 合併所有 chunk 的文字
        full_text = "\n".join(doc.page_content for doc in documents)

        if len(full_text) < 3000:
            return await self._direct_summarize(full_text, max_length)
        else:
            return await self._map_reduce_summarize(
                documents, max_length
            )

    async def _direct_summarize(
        self, text: str, max_length: int
    ) -> str:
        """短文件直接摘要"""
        messages = [
            SystemMessage(content=(
                "你是一位企業知識管理專家。請為以下文件產生一份簡潔的摘要。"
                f"摘要長度不超過 {max_length} 字。"
                "摘要應包含：文件主題、核心要點、關鍵結論。"
                "使用繁體中文撰寫。"
            )),
            HumanMessage(content=f"請摘要以下文件：\n\n{text}"),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content

    async def _map_reduce_summarize(
        self, documents: list[Document], max_length: int
    ) -> str:
        """長文件使用 Map-Reduce 策略"""
        # === Map 階段：每個 chunk 產生小摘要 ===

        chunk_summaries = []

        for doc in documents:
            messages = [
                SystemMessage(content=(
                    "請用 2-3 句話摘要以下文字段落的核心要點。"
                    "使用繁體中文。"
                )),
                HumanMessage(content=doc.page_content),
            ]

            response = await self.llm.ainvoke(messages)
            chunk_summaries.append(response.content)

        # === Reduce 階段：合併為最終摘要 ===
        combined = "\n\n".join(
            f"段落 {i+1} 摘要：{s}"
            for i, s in enumerate(chunk_summaries)
        )

        messages = [
            SystemMessage(content=(
                "以下是一份文件各段落的摘要。"
                f"請將它們整合為一份不超過 {max_length} 字的完整摘要。"
                "摘要應涵蓋文件的主題、核心要點和關鍵結論。"
                "使用繁體中文撰寫。"
            )),
            HumanMessage(content=combined),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content
