# demo6.py
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import numpy as np

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# 準備三段文字
text_a = "我喜歡喝咖啡"
text_b = "我愛喝拿鐵"
text_c = "今天的股市表現不錯"

# 嵌入它們
vectors = embeddings.embed_documents([text_a, text_b, text_c])
vec_a, vec_b, vec_c = np.array(vectors[0]), np.array(vectors[1]), np.array(vectors[2])

# 計算餘弦相似度
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print(f"'{text_a}' vs '{text_b}': {cosine_similarity(vec_a, vec_b):.4f}")

# 預期：較高的相似度（都在講喝飲料）
print(f"'{text_a}' vs '{text_c}': {cosine_similarity(vec_a, vec_c):.4f}")

# 預期：較低的相似度（主題完全不同）
print(f"'{text_b}' vs '{text_c}': {cosine_similarity(vec_b, vec_c):.4f}")
