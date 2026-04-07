# src/config.py

"""企業文件問答系統 — 全域設定"""

from dotenv import load_dotenv
load_dotenv()

import os

# ── LLM 設定 ──
PRIMARY_MODEL = "anthropic:claude-sonnet-4-6"
GRAPH_EXTRACTION_MODEL = "anthropic:claude-sonnet-4-6"

# ── Embedding 設定 ──
EMBEDDING_MODEL = "models/gemini-embedding-001"

# ── Neo4j 設定 ──
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# ── Chroma 設定 ──
CHROMA_PERSIST_DIR = "./data/chroma_db"
CHROMA_COLLECTION_NAME = "enterprise_docs"

# ── 文件切割設定 ──
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ── 檢索設定 ──
VECTOR_SEARCH_K = 5
GRAPH_SEARCH_K = 3
