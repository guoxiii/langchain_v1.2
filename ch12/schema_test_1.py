# schema_test_1.py

"""LLMGraphTransformer 基本使用 -- 無 Schema 模式"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

load_dotenv()

# 初始化 LLM（使用 Gemini）
llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

# 建立 LLMGraphTransformer（無 Schema，自由提取）
llm_transformer = LLMGraphTransformer(llm=llm)

# 準備測試文件
text = """
張三是研發部的資深工程師，他的主管是李四。
李四同時擔任研發部的經理，負責管理 AI 專案和資料平台專案。
AI 專案使用了 Python 和 LangChain 技術。
王五是市場部的經理，他跟李四經常合作推動跨部門的 AI 行銷專案。
"""

doc = Document(page_content=text)

# 轉換為 Graph Document
graph_documents = llm_transformer.convert_to_graph_documents([doc])
# 查看結果
graph_doc = graph_documents[0]

print("=== 節點（Nodes）===")

for node in graph_doc.nodes:
    print(f"  {node.id} (Label: {node.type})")

print("\n=== 關係（Relationships）===")

for rel in graph_doc.relationships:
    print(f"  {rel.source.id} -[{rel.type}]-> {rel.target.id}")