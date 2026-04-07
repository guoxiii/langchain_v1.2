# load_webpage.py
from langchain_community.document_loaders import WebBaseLoader

# 載入單一網頁
loader = WebBaseLoader("https://python.langchain.com/docs/concepts/rag/")
docs = loader.load()

print(f"載入了 {len(docs)} 個 Document")
print(f"內容前 300 字：{docs[0].page_content[:300]}")
print(f"來源：{docs[0].metadata['source']}")
