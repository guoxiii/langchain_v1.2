# ch10/faiss_merge.py
"""合併多個 FAISS 索引"""
from dotenv import load_dotenv

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 第一批文件
docs_batch1 = [
    Document(page_content="台北是台灣的首都。"),
    Document(page_content="台中以太陽餅聞名。"),
]

# 第二批文件
docs_batch2 = [
    Document(page_content="高雄是台灣的港都。"),
    Document(page_content="花蓮的太魯閣峽谷壯觀無比。"),
]

# 分別建立索引
store1 = FAISS.from_documents(docs_batch1, embeddings)
store2 = FAISS.from_documents(docs_batch2, embeddings)

print(f"Store 1 向量數：{store1.index.ntotal}")
print(f"Store 2 向量數：{store2.index.ntotal}")

# 合併
store1.merge_from(store2)
print(f"合併後向量數：{store1.index.ntotal}")

# 驗證：搜尋第二批的內容
results = store1.similarity_search("台灣的港口城市", k=1)
print(f"\n🔍 搜尋結果：{results[0].page_content}")
