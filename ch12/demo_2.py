# demo_2.py
"""模式三：社群摘要（概念示範）"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_neo4j import Neo4jGraph

load_dotenv()

llm = init_chat_model("google_genai:gemini-2.5-flash")

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 步驟 1：使用 Cypher 建立社群（簡化版）
# 實際上你可能需要使用 Neo4j 的 Graph Data Science 套件來執行 Leiden 演算法
# 這裡用部門作為天然的「社群」分組

communities = graph.query("""
    MATCH (p:Person)-[:BELONGS_TO]->(d:Department)
    OPTIONAL MATCH (p)-[:WORKS_ON]->(proj:Project)
    OPTIONAL MATCH (p)-[:MANAGES]->(managed)
    RETURN d.id AS community,
           collect(DISTINCT p.id) AS members,
           collect(DISTINCT proj.id) AS projects,
           collect(DISTINCT labels(managed)[0]) AS manages_types
""")

# 步驟 2：為每個社群生成摘要
for community in communities:
    summary_prompt = f"""
    請為以下部門社群生成一段簡短的摘要：    
    部門：{community['community']}
    成員：{community['members']}
    參與專案：{community['projects']}
    """

    summary = llm.invoke(summary_prompt)

    print(f"\n【{community['community']}】")
    print(summary.content)
