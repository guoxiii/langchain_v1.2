# qa_3.py
"""使用 Enhanced Schema 提升 Cypher 生成準確度"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

load_dotenv()

llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

# 使用 Enhanced Schema（包含屬性值範例）
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    enhanced_schema=True,  # 這會讓 Schema 包含屬性值範例
)

cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
)

# Enhanced Schema 可以幫助 LLM 知道有哪些具體的值可以查詢
# 例如：LLM 會知道 Person 節點有 "張三"、"李四" 等名字

response = cypher_chain.invoke({"query": "張三在哪個部門工作？"})
print(f"回答：{response['result']}")
