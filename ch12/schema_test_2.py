# schema_test_2.py

"""LLMGraphTransformer 進階使用 -- 指定 Schema"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

load_dotenv()

llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

# 指定允許的節點類型和關係類型
llm_transformer = LLMGraphTransformer(
    llm=llm,
    # 只提取這些類型的節點
    allowed_nodes=["Person", "Department", "Project", "Technology"],
    # 只提取這些類型的關係
    allowed_relationships=[
        "BELONGS_TO",      # 人隸屬於部門
        "MANAGES",         # 人管理部門/專案
        "WORKS_ON",        # 人參與專案
        "REPORTS_TO",      # 人的上級
        "USES",            # 專案使用技術
        "COLLABORATES_WITH" # 協作關係
    ],

    # 提取節點的額外屬性
    node_properties=["title", "description"],
    # 提取關係的額外屬性
    relationship_properties=["role", "since"],
)

text = """
張三是研發部的資深工程師，自 2021 年起擔任 AI 專案的技術負責人。
他的直屬主管是李四，李四是研發部的經理。
AI 專案主要使用 Python 和 LangChain 技術來開發智能客服系統。
市場部的王五經理與李四密切合作，共同推動 AI 行銷專案。
"""

doc = Document(page_content=text)
graph_documents = llm_transformer.convert_to_graph_documents([doc])
graph_doc = graph_documents[0]

print("=== 節點 ===")

for node in graph_doc.nodes:
    props = {k: v for k, v in node.properties.items() if v}
    print(f"  {node.id} ({node.type}) {props if props else ''}")

print("\n=== 關係 ===")

for rel in graph_doc.relationships:
    props = {k: v for k, v in rel.properties.items() if v}
    print(f"  {rel.source.id} -[{rel.type}]-> {rel.target.id} {props if props else ''}")