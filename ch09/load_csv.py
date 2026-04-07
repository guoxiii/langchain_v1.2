# load_csv.py
from langchain_community.document_loaders.csv_loader import CSVLoader

# 載入 CSV
loader = CSVLoader("./documents/products.csv", encoding="utf-8")
docs = loader.load()

print(f"共載入 {len(docs)} 列（每列一個 Document）")
print(f"第一列內容：{docs[0].page_content}")
print(f"第一列 metadata：{docs[0].metadata}")
