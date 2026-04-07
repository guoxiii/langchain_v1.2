# ch_demo.py
"""
實作練習：企業組織架構 GraphRAG 問答系統
=========================================

此系統整合了：
- LLMGraphTransformer：自動從文件建構知識圖譜
- Neo4jGraph：圖資料庫操作
- Neo4jVector：向量搜尋
- GraphCypherQAChain：自然語言轉 Cypher
- create_agent：Agent 架構整合

使用前請確認：
1. Neo4j 已啟動（Aura Free 或 Docker）
2. .env 檔案已設定 NEO4J_URI、NEO4J_USERNAME、NEO4J_PASSWORD、GOOGLE_API_KEY
3. 已安裝所需套件：uv add langchain langchain-neo4j langchain-experimental
   langchain-google-genai
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain, Neo4jVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()


# ============================================================
# 輔助函式：提取 AI 訊息的純文字內容
# ============================================================

def extract_text(ai_message) -> str:
    """從 AI 訊息中提取純文字內容。

    Gemini 模型回傳的 content 有時是 list[dict]（包含 type/text/extras），
    而非單純的字串，此函式統一處理兩種情況。
    """

    content = ai_message.content

    if isinstance(content, str):
        return content

    # content 為 list[dict] 時，提取所有 text 區塊
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block["text"])
            elif isinstance(block, str):
                texts.append(block)
        return "\n".join(texts)

    return str(content)


# ============================================================
# 第一步：準備資料與建構知識圖譜
# ============================================================

print("📊 步驟 1：初始化元件...")

# 初始化 LLM
llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

# 初始化 Embedding 模型
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
)

# 連接 Neo4j
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 清空現有資料（開發環境用，生產環境請勿使用！）
graph.query("MATCH (n) DETACH DELETE n")

# ============================================================
# 第二步：準備企業組織架構的文件
# ============================================================

print("📄 步驟 2：準備組織架構文件...")

org_documents = [
    Document(
        page_content="""
        陳大明是科技長（CTO），直接向執行長趙總報告。
        陳大明負責管理研發部和技術架構部兩個部門。
        他自 2019 年加入公司，擁有 20 年的軟體開發經驗。
        """,
        metadata={"source": "org_chart", "department": "高階管理"}
    ),
    Document(
        page_content="""
        張三是研發部的資深工程師，自 2021 年加入公司。
        他目前擔任 AI 智能客服專案的技術負責人。
        張三的直屬主管是研發部經理李四。
        AI 智能客服專案使用 Python、LangChain 和 Neo4j 技術。
        """,
        metadata={"source": "org_chart", "department": "研發部"}
    ),
    Document(
        page_content="""
        李四是研發部的經理，自 2018 年加入公司。
        他管理研發部的三個專案：AI 智能客服專案、資料平台專案和行動應用專案。
        李四向科技長陳大明直接報告。

        資料平台專案使用 Apache Spark 和 PostgreSQL 技術。
        行動應用專案使用 Flutter 和 Firebase 技術。
        """,
        metadata={"source": "org_chart", "department": "研發部"}
    ),
    Document(
        page_content="""
        王五是市場部的經理，負責品牌行銷專案和社群經營專案。
        品牌行銷專案的目標是提升公司在 AI 領域的知名度。
        王五與研發部的李四密切合作，共同推動 AI 技術的市場推廣。
        市場部的小花負責社群經營專案的日常運營。
        """,
        metadata={"source": "org_chart", "department": "市場部"}
    ),
    Document(
        page_content="""
        技術架構部由架構師趙六領導，他負責制定公司的技術標準和架構規範。
        趙六管理基礎架構專案，該專案負責公司的雲端基礎設施。
        基礎架構專案使用 Kubernetes、Docker 和 AWS 技術。
        趙六向科技長陳大明報告。
        """,
        metadata={"source": "org_chart", "department": "技術架構部"}
    ),
]

# ============================================================
# 第三步：用 LLM 提取知識圖譜
# ============================================================

print("🧠 步驟 3：使用 LLM 提取知識圖譜...")

llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Department", "Project", "Technology"],
    allowed_relationships=[
        "BELONGS_TO",          # 人隸屬於部門
        "MANAGES",             # 人管理部門/專案
        "WORKS_ON",            # 人參與專案
        "REPORTS_TO",          # 人的上級
        "USES",                # 專案使用技術
        "COLLABORATES_WITH",   # 協作關係
        "LEADS",               # 領導
    ],
    node_properties=["title", "join_year", "experience"],
    relationship_properties=["role", "since"],
)

graph_documents = llm_transformer.convert_to_graph_documents(org_documents)

# 統計
total_nodes = sum(len(gd.nodes) for gd in graph_documents)
total_rels = sum(len(gd.relationships) for gd in graph_documents)

print(f"   提取了 {total_nodes} 個節點、{total_rels} 條關係")

# ============================================================
# 第四步：存入 Neo4j
# ============================================================

print("💾 步驟 4：將知識圖譜存入 Neo4j...")

graph.add_graph_documents(
    graph_documents,
    include_source=True,
)

graph.refresh_schema()
print(f"   Schema:\n{graph.schema}")

# ============================================================
# 第五步：建立向量索引
# ============================================================

print("🔍 步驟 5：建立向量索引...")

vector_store = Neo4jVector.from_documents(
    org_documents,
    embeddings,
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="org_doc_vectors",
    node_label="OrgDocument",
    text_node_property="text",
    embedding_node_property="embedding",
)

print("   向量索引建立完成！")

# ============================================================
# 第六步：建立 Agent 工具
# ============================================================

print("🛠️ 步驟 6：建立 Agent 工具...")

# 工具 1：Cypher 查詢（結構化問題）
cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=False,
    allow_dangerous_requests=True,
)


@tool
def query_knowledge_graph(question: str) -> str:
    """用於查詢企業組織架構的知識圖譜。
    適合回答結構化問題，例如：
    - 某人的主管是誰
    - 某部門有哪些成員
    - 某專案使用哪些技術
    - 某人負責哪些專案
    """

    try:
        result = cypher_chain.invoke({"query": question})
        return result.get("result", "查詢無結果")
    except Exception as e:
        return f"查詢知識圖譜時發生錯誤：{str(e)}"


# 工具 2：向量搜尋（語義問題）
@tool
def search_org_documents(query: str) -> str:
    """用於語義搜尋企業組織文件。
    適合回答需要上下文理解的問題，例如：
    - 跟 AI 相關的工作有哪些
    - 公司的技術方向是什麼
    - 某個人的背景經歷
    """

    results = vector_store.similarity_search(query, k=3)

    if not results:
        return "找不到相關文件"
    return "\n\n".join([
        f"[文件 {i+1}]\n{doc.page_content.strip()}"
        for i, doc in enumerate(results)
    ])


# 工具 3：子圖擷取（探索性問題）
@tool
def explore_entity_relations(entity_name: str) -> str:
    """探索某個實體（人名、部門名、專案名）周圍的所有關係。
    適合回答探索性問題，例如：
    - 李四的工作範圍是什麼
    - 研發部的完整資訊
    - AI 智能客服專案的所有相關資訊
    """

    result = graph.query("""
        MATCH (start {id: $name})-[r]-(connected)
        RETURN start.id AS entity,
               type(r) AS relationship,
               CASE
                   WHEN startNode(r) = start THEN '-->'
                   ELSE '<--'
               END AS direction,
               connected.id AS connected_entity,
               labels(connected) AS connected_type
        LIMIT 20
    """, params={"name": entity_name})

    if not result:
        return f"找不到名為 '{entity_name}' 的實體"

    lines = [f"📊 {entity_name} 的關係網："]

    for row in result:
        direction = row["direction"]
        connected_type = row["connected_type"][0] if row["connected_type"] else "?"

        lines.append(
            f"  {row['entity']} {direction} "
            f"[{row['relationship']}] {direction} "
            f"{connected_type}: {row['connected_entity']}"
        )

    return "\n".join(lines)


# ============================================================
# 第七步：建立 Agent
# ============================================================

print("🤖 步驟 7：建立 GraphRAG Agent...")
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[
        query_knowledge_graph,
        search_org_documents,
        explore_entity_relations,
    ],
    system_prompt="""你是一位企業組織架構的 AI 顧問。你可以使用以下工具來回答問題：
1. query_knowledge_graph：查詢知識圖譜中的結構化資訊（人員關係、部門結構、專案分配等）
2. search_org_documents：語義搜尋組織文件，獲取上下文資訊
3. explore_entity_relations：探索某個實體的所有關聯關係

回答原則：
- 使用繁體中文回答
- 如果一個工具的結果不夠完整，可以嘗試其他工具補充
- 回答要清楚、有條理
- 如果確實找不到資訊，誠實告知使用者
""",
    checkpointer=MemorySaver(),
)

# ============================================================
# 第八步：測試！
# ============================================================

print("\n✅ GraphRAG 問答系統已就緒！開始測試...\n")
print("=" * 60)

test_questions = [
    "研發部有哪些成員？他們各自負責什麼？",
    "張三的主管的主管是誰？",
    "哪些專案使用了 Python？",
    "李四和王五之間有什麼關聯？",
    "公司有哪些部門？各部門的專案數量如何？",
]

config = {"configurable": {"thread_id": "graphrag-test"}}

for question in test_questions:
    print(f"\n🙋 問題：{question}")
    print("-" * 40)

    response = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )

    # 取得最後一條 AI 訊息，使用 extract_text() 處理內容格式
    ai_message = response["messages"][-1]
    print(f"🤖 回答：{extract_text(ai_message)}")
    print("=" * 60)