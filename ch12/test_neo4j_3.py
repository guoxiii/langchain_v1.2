# test_neo4j_3.py
"""完整流程：提取知識圖譜並存入 Neo4j"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph

load_dotenv()

# ---- 1. 初始化 LLM 和 Graph Transformer ----
llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)
llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Department", "Project", "Technology"],
    allowed_relationships=[
        "BELONGS_TO", "MANAGES", "WORKS_ON",
        "REPORTS_TO", "USES", "COLLABORATES_WITH"
    ],
)

# ---- 2. 準備文件 ----
documents = [
    Document(page_content="""
    張三是研發部的資深工程師，自 2021 年加入公司。
    他目前是 AI 專案的技術負責人，直屬主管是李四。
    AI 專案使用 Python、LangChain 和 Neo4j 技術。
    """),
    Document(page_content="""
    李四擔任研發部經理，管理研發部的所有專案。
    他同時負責 AI 專案和資料平台專案。
    資料平台專案使用 Apache Spark 和 PostgreSQL。
    """),
    Document(page_content="""
    王五是市場部的經理，負責品牌行銷專案。
    他經常與研發部的李四合作，推動技術驅動的行銷策略。
    """),
]

# ---- 3. 用 LLM 提取知識圖譜 ----

graph_documents = llm_transformer.convert_to_graph_documents(documents)
# 打印提取結果

for i, gd in enumerate(graph_documents):
    print(f"\n--- 文件 {i+1} ---")
    print(f"  節點: {[n.id for n in gd.nodes]}")
    print(f"  關係: {[(r.source.id, r.type, r.target.id) for r in gd.relationships]}")

# ---- 4. 存入 Neo4j ----
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 使用 add_graph_documents 將提取結果存入 Neo4j
# include_source=True 會將原始文件也存為節點，並建立 MENTIONS 關係
graph.add_graph_documents(
    graph_documents,
    include_source=True,  # 保留來源文件的追蹤
)

print("\n✅ 知識圖譜已成功存入 Neo4j！")

# ---- 5. 驗證 ----
# 查看存入的節點數量

result = graph.query("""
    MATCH (n)
    RETURN labels(n) AS label, count(n) AS count
    ORDER BY count DESC
""")

print("\n=== 資料庫統計 ===")

for row in result:
    print(f"  {row['label']}: {row['count']} 個")

# 查看存入的關係
result = graph.query("""
    MATCH ()-[r]->()
    RETURN type(r) AS relationship, count(r) AS count
    ORDER BY count DESC
""")

print("\n=== 關係統計 ===")

for row in result:
    print(f"  {row['relationship']}: {row['count']} 條")
