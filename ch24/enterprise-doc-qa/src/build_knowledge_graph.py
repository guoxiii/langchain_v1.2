# build_knowledge_graph.py

"""建構知識圖譜 — 端到端流程"""

from dotenv import load_dotenv
load_dotenv()
from src.document_pipeline import DocumentPipeline
from src.knowledge_graph import KnowledgeGraphBuilder

# Step 1: 處理文件
pipeline = DocumentPipeline()

chunks = pipeline.process([
    {
        "source": "docs/employee_handbook.pdf",
        "department": "hr",
        "access_level": "internal",
    },
    {
        "source": "docs/product_spec.docx",
        "department": "engineering",
        "access_level": "confidential",
    },
    {
        "source": "https://www.tsmc.com/chinese/aboutTSMC/mission",
        "department": "marketing",
        "access_level": "public",
    },
])

# Step 2: 建構知識圖譜
kg_builder = KnowledgeGraphBuilder()

# 先清空舊資料（僅開發環境）
kg_builder.clear_graph()

# 建構圖譜
stats = kg_builder.build_from_documents(chunks)

# Step 3: 驗證結果
print("\n📋 圖譜 Schema：")
print(kg_builder.get_schema())

# 查看一些範例節點
results = kg_builder.query_graph(
    "MATCH (n) RETURN labels(n) AS labels, n.id AS name LIMIT 10"
)
print("\n📌 範例節點：")

for r in results:
    print(f"   {r['labels']}: {r['name']}")
