# demo7.py
import os
from dotenv import load_dotenv
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# 1. 準備「知識庫」（假裝這些是從文件載入 + 切割後的 chunks）
knowledge_base = [
    "本公司退貨政策：商品可在購買後 30 天內無條件退貨，需保留原始包裝。",
    "會員制度分為三級：銅卡、銀卡、金卡，消費累積越多等級越高。",
    "客服電話：0800-123-456，服務時間為週一至週五 9:00-18:00。",
    "免運門檻：單筆消費滿 1000 元即可享有免運費優惠。",
    "商品保固：電子產品享有一年原廠保固，耗材類不在保固範圍。",
]

# 2. 建立 Embedding 模型
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# 3. 嵌入所有知識庫文件
doc_vectors = embeddings.embed_documents(knowledge_base)

# 4. 使用者提問
query = "如果東西壞了可以換嗎？"
query_vector = embeddings.embed_query(query)

# 5. 計算相似度
def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

similarities = []

for i, doc_vec in enumerate(doc_vectors):
    sim = cosine_similarity(query_vector, doc_vec)
    similarities.append((i, sim))

# 6. 按相似度排序，取 Top 2
similarities.sort(key=lambda x: x[1], reverse=True)

print(f"使用者問題：{query}\n")
print("語義搜尋結果（Top 2）：")

for rank, (idx, sim) in enumerate(similarities[:2], 1):
    print(f"  #{rank} (相似度 {sim:.4f}): {knowledge_base[idx]}")
