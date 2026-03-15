# ch10/inmemory_basic.py
"""InMemoryVectorStore 基本用法示範"""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# 初始化 Embedding 模型（沿用第 9 章的設定）
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# 建立 InMemoryVectorStore
vector_store = InMemoryVectorStore(embedding=embeddings)

# 準備文件
documents = [
    Document(
        id="1",
        page_content="台南是台灣的古都，擁有豐富的歷史古蹟和美食文化。赤崁樓、安平古堡都是必訪景點。",
        metadata={"city": "台南", "category": "歷史"}
    ),
    Document(
        id="2",
        page_content="台北101是台灣最知名的地標建築，樓高508公尺，曾是世界最高建築。觀景台可以俯瞰整個台北市。",
        metadata={"city": "台北", "category": "地標"}
    ),
    Document(
        id="3",
        page_content="日月潭位於南投縣，是台灣最大的天然湖泊。周圍群山環繞，風景秀麗，是著名的觀光景點。",
        metadata={"city": "南投", "category": "自然"}
    ),
    Document(
        id="4",
        page_content="台南牛肉湯是當地最具代表性的早餐，使用新鮮溫體牛肉搭配清甜湯頭，天還沒亮就大排長龍。",
        metadata={"city": "台南", "category": "美食"}
    ),
    Document(
        id="5",
        page_content="墾丁國家公園位於屏東縣，擁有美麗的珊瑚礁海岸和豐富的生態資源，是台灣著名的度假勝地。",
        metadata={"city": "屏東", "category": "自然"}
    ),
]

# 將文件加入 Vector Store
vector_store.add_documents(documents=documents)

print(f"✅ 已加入 {len(documents)} 筆文件")

# 進行相似度搜尋

query = "台灣有什麼好吃的？"
results = vector_store.similarity_search(query=query, k=2)

print(f"\n🔍 搜尋：「{query}」")
print("-" * 50)

for i, doc in enumerate(results, 1):
    print(f"\n📄 結果 {i}:")
    print(f"   內容：{doc.page_content[:60]}...")
    print(f"   城市：{doc.metadata.get('city')}")
    print(f"   分類：{doc.metadata.get('category')}")
