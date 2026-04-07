# src/config.py
"""KnowledgeHub 全域設定"""

from dotenv import load_dotenv
load_dotenv()

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    """應用程式設定 — frozen=True 確保不可變"""
    # AI 模型
    primary_model: str = "google_genai:gemini-2.5-flash"
    fallback_model: str = "anthropic:claude-sonnet-4-6"
    embedding_model: str = "models/gemini-embedding-001"

    # 向量資料庫
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    chroma_collection: str = "knowledge_hub_docs"

    # Neo4j
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")

    # PostgreSQL
    postgres_uri: str = os.getenv("POSTGRES_URI", "")

    # 文件處理
    upload_dir: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # RAG
    retriever_k: int = 5
    retriever_search_type: str = "mmr"


# 全域單例
config = AppConfig()
