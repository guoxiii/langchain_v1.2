# test_neo4j.py
# 驗證 Neo4j 連線

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

# 建立 Neo4j 連線
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 測試查詢
result = graph.query("RETURN 'Hello, Neo4j!' AS message")
print(result)

# 輸出：[{'message': 'Hello, Neo4j!'}]
# 查看資料庫 Schema
print(graph.schema)

# 如果是空的資料庫，會顯示 "Node properties are the following: ..."