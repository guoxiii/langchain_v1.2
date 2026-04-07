# test_pipeline.py

"""測試文件處理管線"""

from dotenv import load_dotenv
load_dotenv()

from src.document_pipeline import DocumentPipeline
pipeline = DocumentPipeline()

# 假設你有這些測試文件
chunks = pipeline.process([
    {
        "source": "docs/company_policy.pdf",
        "department": "hr",
        "access_level": "internal",
    },
    {
        "source": "docs/api_guide.docx",
        "department": "engineering",
        "access_level": "confidential",
    },
])

# 檢查結果
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i} ---")
    print(f"內容前 100 字：{chunk.page_content[:100]}...")
    print(f"Metadata：{chunk.metadata}")
