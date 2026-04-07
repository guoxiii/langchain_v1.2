# demo_1.py
"""模式二：向量搜尋 + 圖譜擴展"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
)

def vector_then_graph(question: str, graph: Neo4jGraph) -> str:
    """向量搜尋找起點，圖譜擴展找關聯"""
    query_embedding = embeddings.embed_query(question)

    # 步驟 1：向量搜尋找到最相關的實體
    vector_results = graph.query("""
        CALL db.index.vector.queryNodes('document_vectors', 3, $embedding)
        YIELD node, score
        RETURN node.text AS text, score
        ORDER BY score DESC
    """, params={"embedding": query_embedding})

    # 步驟 2：從結果中找到提到的實體，擴展圖譜查詢
    # （這裡簡化為查詢所有 Project 節點的相關人員）
    graph_expansion = graph.query("""
        MATCH (p:Person)-[r:WORKS_ON|MANAGES]->(proj:Project)
        OPTIONAL MATCH (proj)-[:USES]->(tech:Technology)
        RETURN p.id AS person,
               type(r) AS role,
               proj.id AS project,
               collect(DISTINCT tech.id) AS technologies
    """)

    return {
        "vector_context": vector_results,
        "graph_context": graph_expansion,
    }

result = vector_then_graph("AI 相關的技術和負責人", graph)

print("向量結果:", result["vector_context"])
print("圖譜擴展:", result["graph_context"])
