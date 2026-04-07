# test_neo4j_2.py
"""Neo4jGraph 基本操作"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

# 建立連線
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 查看資料庫 Schema
print(graph.schema)

# 執行 Cypher 查詢
result = graph.query("MATCH (n) RETURN labels(n) AS labels, count(n) AS count")
print(result)

# 帶參數的查詢（防止 Cypher Injection）
result = graph.query(
    "MATCH (p:Person {name: $name}) RETURN p",
    params={"name": "張三"}
)

print(result)
