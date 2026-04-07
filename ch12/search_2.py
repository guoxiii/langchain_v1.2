# search_2.py
"""Neo4j 混合搜尋（向量 + 關鍵字）"""

import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
)

docs = [
    Document(page_content="張三是研發部的資深工程師，負責 AI 專案的技術開發。"),
    Document(page_content="李四是研發部的經理，管理 AI 專案和資料平台專案。"),
    Document(page_content="王五是市場部的經理，負責品牌行銷和客戶關係管理。"),
]

# 建立混合搜尋（向量 + 關鍵字）
hybrid_store = Neo4jVector.from_documents(
    docs,
    embeddings,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="hybrid_index",
    node_label="HybridChunk",
    search_type="hybrid",  # 啟用混合搜尋
)

# 混合搜尋會同時使用向量相似度和關鍵字匹配
results = hybrid_store.similarity_search("研發部 AI 專案", k=3)

for doc in results:
    print(f"  {doc.page_content}")
