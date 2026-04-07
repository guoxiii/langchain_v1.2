# qa_2.py
"""GraphCypherQAChain 自定義 Prompt"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

load_dotenv()

llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# 自定義 Cypher 生成 Prompt
CYPHER_GENERATION_TEMPLATE = """你是一個 Neo4j Cypher 查詢專家。
根據以下的圖資料庫 Schema，將使用者的自然語言問題轉換為 Cypher 查詢語句。

Schema：
{schema}

注意事項：
1. 只使用 Schema 中存在的節點類型和關係類型
2. 只使用 MATCH 和 RETURN，不要使用 CREATE、DELETE、SET 等修改操作
3. 如果問題涉及數量統計，使用 count() 函式
4. 中文名稱要完全匹配

以下是一些範例：
# 查詢某個部門的所有成員
MATCH (p:Person)-[:BELONGS_TO]->(d:Department {{name: "研發部"}})
RETURN p.name AS name, p.title AS title

# 查詢某人的主管
MATCH (p:Person {{name: "張三"}})-[:REPORTS_TO]->(m:Person)
RETURN m.name AS manager_name

使用者問題：{question}

只回覆 Cypher 查詢語句，不要包含任何解釋。"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE,
)

# 自定義回答生成 Prompt
QA_GENERATION_TEMPLATE = """你是一個友善的 AI 助理，根據以下資料庫查詢結果來回答使用者的問題。
如果查詢結果為空，請告訴使用者找不到相關資訊。
請用繁體中文回答。

查詢結果：{context}
使用者問題：{question}
回答："""

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_GENERATION_TEMPLATE,
)

# 使用自定義 Prompt 建立 Chain
cypher_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True,
    cypher_prompt=cypher_prompt,     # 自定義 Cypher 生成 Prompt
    qa_prompt=qa_prompt,             # 自定義回答生成 Prompt
)

# 測試不同的問題
questions = [
    "研發部有哪些成員？",
    "張三的主管是誰？",
    "李四負責哪些專案？",
    "哪些專案使用了 Python？",
    "市場部跟哪個部門有合作？",
]

for q in questions:
    print(f"\n{'='*50}")
    print(f"問題：{q}")
    response = cypher_chain.invoke({"query": q})
    print(f"回答：{response['result']}")
