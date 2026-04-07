# proc_multi_doc.py

"""批量處理多份文件"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

load_dotenv()

llm = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
)

llm_transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Department", "Project"],
    allowed_relationships=["BELONGS_TO", "MANAGES", "WORKS_ON", "REPORTS_TO"],
)

# 模擬多份文件
documents = [
    Document(
        page_content="張三是研發部的工程師，負責 AI 專案。他的主管是李四。",
        metadata={"source": "hr_doc_001"}
    ),
    Document(
        page_content="李四是研發部的經理，同時兼管資料平台專案。",
        metadata={"source": "hr_doc_002"}
    ),
    Document(
        page_content="王五是市場部經理，負責品牌行銷專案。他跟李四協作推動 AI 行銷。",
        metadata={"source": "hr_doc_003"}
    ),
]

# 批量轉換
all_graph_docs = llm_transformer.convert_to_graph_documents(documents)

# 統計結果
total_nodes = sum(len(gd.nodes) for gd in all_graph_docs)
total_rels = sum(len(gd.relationships) for gd in all_graph_docs)

print(f"從 {len(documents)} 份文件中提取了 {total_nodes} 個節點、{total_rels} 條關係")