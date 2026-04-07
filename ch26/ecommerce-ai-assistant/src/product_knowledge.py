# src/product_knowledge.py

"""
商品知識庫建構模組
將商品資料同時向量化（Chroma）與圖譜化（Neo4j）
"""

import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def load_products(file_path: str = "data/products.json") -> list[dict]:
    """載入商品資料"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_product_documents(products: list[dict]) -> list[Document]:
    """
    將商品資料轉換為 LangChain Document 物件。
    這裡的關鍵技巧是：把商品的所有資訊「攤平」成一段自然語言描述，
    讓 Embedding 模型能充分理解商品的語義。
    就像把一張商品規格表改寫成一段導購員的介紹詞。
    """

    documents = []

    for product in products:
        # 組合成豐富的文字描述，讓 Embedding 能捕捉更多語義
        content = f"""
商品名稱：{product['name']}
商品編號：{product['id']}
類別：{product['category']} > {product['subcategory']}
價格：NT${product['price']}
商品描述：{product['description']}
主要成分：{', '.join(product['ingredients'])}
適用膚質：{', '.join(product['skin_type'])}
特色標籤：{', '.join(product['tags'])}
評分：{product['rating']}/5.0
庫存：{product['stock']} 件
""".strip()

        doc = Document(
            page_content=content,
            metadata={
                "product_id": product["id"],
                "name": product["name"],
                "category": product["category"],
                "subcategory": product["subcategory"],
                "price": product["price"],
                "rating": product["rating"],
                "stock": product["stock"],
                "skin_type": ",".join(product["skin_type"]),
                "tags": ",".join(product["tags"]),
            },
        )

        documents.append(doc)
    return documents

def build_vector_store(
    documents: list[Document],
    persist_directory: str = "./chroma_products",
) -> Chroma:
    """
    建立商品向量資料庫。
    使用 Google 的 Embedding 模型將商品描述轉為向量，
    存入 Chroma 向量資料庫。
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name="products",
    )

    print(f"✅ 已建立向量資料庫，共 {len(documents)} 筆商品")
    return vector_store

def get_vector_store(
    persist_directory: str = "./chroma_products",
) -> Chroma:
    """載入已存在的向量資料庫"""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
    )

    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name="products",
    )

# ============================================================
# 執行建構
# ============================================================
if __name__ == "__main__":
    products = load_products()
    documents = create_product_documents(products)
    vector_store = build_vector_store(documents)

    # 測試搜尋
    results = vector_store.similarity_search("我想要控油的保養品", k=3)
    print("\n🔍 搜尋「控油保養品」的結果：")

    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.metadata['name']} (相關度排名 #{i})")
