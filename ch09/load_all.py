# load_all.py
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    CSVLoader
)

all_docs = []

# 載入所有 PDF
pdf_loader = DirectoryLoader("./documents", glob="**/*.pdf", loader_cls=PyPDFLoader)
all_docs.extend(pdf_loader.load())

# 載入所有 TXT
txt_loader = DirectoryLoader(
    "./documents",
    glob="**/*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
all_docs.extend(txt_loader.load())


# 載入所有 CSV
csv_loader = DirectoryLoader(
    "./documents",
    glob="**/*.csv",
    loader_cls=CSVLoader,
    loader_kwargs={"encoding": "utf-8"}
)
all_docs.extend(csv_loader.load())

print(f"總共載入 {len(all_docs)} 個 Document")
