# search_3.py
"""GraphRAG 核心：Vector + Graph 混合檢索"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
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


def graphrag_retrieval(question: str, graph: Neo4jGraph, k: int = 3) -> str:
    """
    GraphRAG 混合檢索：
    1. 先用向量搜尋找到相關的文件片段
    2. 從片段中提取實體，到圖譜中擴展查詢
    3. 合併兩個來源的資訊
    """

    # 步驟 1：向量搜尋（找到最相關的文件片段）
    vector_results = graph.query(
        """
        CALL db.index.vector.queryNodes('document_vectors', $k, $embedding)
        YIELD node, score
        RETURN node.text AS text, score
        """,
        params={
            "k": k,
            "embedding": embeddings.embed_query(question),
        }
    )

    # 步驟 2：從向量結果中提取實體名稱，查詢圖譜
    # 這裡用一個簡化的方式：查詢所有 Person 節點及其關係

    graph_results = graph.query("""
        MATCH (p:Person)-[r]->(target)
        RETURN p.name AS person,
               type(r) AS relationship,
               labels(target)[0] AS target_type,
               COALESCE(target.name, target.title, '') AS target_name
        LIMIT 20
    """)

    # 步驟 3：組合結果
    context_parts = []

    # 加入向量搜尋結果
    if vector_results:
        context_parts.append("【文件片段（向量搜尋）】")

        for r in vector_results:
            context_parts.append(f"- {r['text']}")

    # 加入圖譜查詢結果
    if graph_results:
        context_parts.append("\n【知識圖譜（關係查詢）】")

        for r in graph_results:
            context_parts.append(
                f"- {r['person']} --[{r['relationship']}]--> "
                f"{r['target_type']}: {r['target_name']}"
            )

    return "\n".join(context_parts)

# 測試
question = "張三的主管負責哪些專案？"
context = graphrag_retrieval(question, graph)

print(context)

# 將 context 餵給 LLM 生成回答
llm = init_chat_model("google_genai:gemini-2.5-flash")

response = llm.invoke(
    f"根據以下資訊回答問題。\n\n資訊：\n{context}\n\n問題：{question}"
)

print(f"\n=== AI 回答 ===\n{response.content}")
