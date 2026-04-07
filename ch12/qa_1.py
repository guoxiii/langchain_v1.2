# qa_1.py
"""GraphCypherQAChain 基本使用"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

load_dotenv()

# 初始化 LLM
llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

# 連接 Neo4j
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 建立 GraphCypherQAChain
cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,               # 顯示生成的 Cypher 和中間過程
    allow_dangerous_requests=True,  # 必須設定，否則會拋出安全警告
)

# 提問
response = cypher_chain.invoke({"query": "研發部有哪些成員？"})

print(f"\n回答：{response['result']}")
