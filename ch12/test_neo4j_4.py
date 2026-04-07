# test_neo4j_4.py
"""Enhanced Schema 模式"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

# 啟用 Enhanced Schema
enhanced_graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    enhanced_schema=True,  # 啟用增強 Schema
)

print(enhanced_graph.schema)
