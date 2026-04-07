# load_dir.py
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

# 載入 ./documents 資料夾下所有 PDF
loader = DirectoryLoader(
    path="./documents/pdfs",
    glob="**/*.pdf",           # 遞迴搜尋所有 PDF
    loader_cls=PyPDFLoader,    # 用 PyPDFLoader 處理每個檔案
    show_progress=True         # 顯示進度條
)

docs = loader.load()
print(f"從整個資料夾載入了 {len(docs)} 個 Document")
