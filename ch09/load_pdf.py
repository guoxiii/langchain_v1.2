# load_pdf.py
from langchain_community.document_loaders import PyPDFLoader

# 建立 Loader，指定 PDF 檔案路徑
loader = PyPDFLoader("./documents/company_handbook.pdf")

# 載入所有頁面
docs = loader.load()

# 看看載入了幾頁
print(f"共載入 {len(docs)} 頁")

# 看看第一頁的內容
print(f"第一頁內容（前 200 字）：{docs[0].page_content[:200]}")

# 看看 metadata
print(f"第一頁 metadata：{docs[0].metadata}")

# 輸出類似：{'source': './documents/company_handbook.pdf', 'page': 0}
