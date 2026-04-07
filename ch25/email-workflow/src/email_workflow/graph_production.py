# src/email_workflow/graph_production.py

"""生產環境的工作流配置 — 使用 PostgresSaver"""

from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.email_workflow.graph import build_workflow

async def compile_production_workflow():
    """
    編譯生產環境工作流
    使用 PostgreSQL 作為 Checkpointer，
    確保即使系統重啟，工作流狀態也不會遺失。
    這就是 Durable Execution 的核心：
    你的工作流像是一隻打不死的蟑螂（好吧，比喻不太雅觀），
    不管你怎麼關機重啟，它都能從斷點繼續。
    """

    db_uri = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/email_workflow"
    )

    async with AsyncPostgresSaver.from_conn_string(db_uri) as checkpointer:
        await checkpointer.setup()  # 建立必要的資料表
        workflow = build_workflow()
        graph = workflow.compile(checkpointer=checkpointer)
        return graph
