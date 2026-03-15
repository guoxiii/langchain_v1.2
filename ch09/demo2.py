# demo2.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 載入 PDF
loader = PyPDFLoader("./documents/company_handbook.pdf")
docs = loader.load()

print(f"載入了 {len(docs)} 頁")

# 2. 切割
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(docs)

print(f"切割後共 {len(chunks)} 個 chunk")

# 3. 每個 chunk 都保留了原始的 metadata
print(f"第一個 chunk 的 metadata：{chunks[0].metadata}")

# 輸出類似：{'source': './documents/company_handbook.pdf', 'page': 0}
