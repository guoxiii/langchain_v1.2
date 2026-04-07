# demo5.py
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 載入環境變數（需要 GOOGLE_API_KEY）
load_dotenv()

# 建立 Embedding 模型
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# 嵌入單一查詢
query_vector = embeddings.embed_query("LangChain 是什麼？")

print(f"向量維度：{len(query_vector)}")

# 輸出：向量維度：3072（gemini-embedding-001 預設維度）
# 看看向量的前 5 個數字
print(f"向量前 5 個值：{query_vector[:5]}")
# 輸出類似：[0.023, -0.156, 0.892, -0.045, 0.567]