# search_1.py
"""Neo4j 向量搜尋"""

import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# 初始化 Embedding 模型
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
)

# 準備文件
docs = [
    Document(page_content="張三是研發部的資深工程師，負責 AI 專案的技術開發。"),
    Document(page_content="李四是研發部的經理，管理 AI 專案和資料平台專案。"),
    Document(page_content="王五是市場部的經理，負責品牌行銷和客戶關係管理。"),
    Document(page_content="AI 專案使用 Python 和 LangChain，目標是建立智能客服系統。"),
    Document(page_content="資料平台專案使用 Apache Spark，負責處理公司的大數據分析。"),
]

# 建立 Neo4j 向量存儲
vector_store = Neo4jVector.from_documents(
    docs,
    embeddings,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="document_vectors",      # 向量索引名稱
    node_label="DocumentChunk",          # 節點標籤
    text_node_property="text",           # 文字屬性名稱
    embedding_node_property="embedding", # 向量屬性名稱
)

# 語義搜尋
query = "誰負責 AI 相關的工作？"
results = vector_store.similarity_search_with_score(query, k=3)

print("=== 向量搜尋結果 ===")

for doc, score in results:
    print(f"  [{score:.4f}] {doc.page_content}")
