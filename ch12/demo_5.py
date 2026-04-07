# demo_5.py
"""模式六：結構化彙總"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 查詢各部門的專案數量
result = graph.query("""
    MATCH (d:Department)<-[:BELONGS_TO]-(p:Person)
    OPTIONAL MATCH (p)-[:WORKS_ON]->(proj:Project)
    RETURN d.id AS department,
           count(DISTINCT p) AS member_count,
           count(DISTINCT proj) AS project_count
    ORDER BY member_count DESC
""")

print("=== 部門統計 ===")

for row in result:
    print(f"  {row['department']}: {row['member_count']} 人, "
          f"{row['project_count']} 個專案")
