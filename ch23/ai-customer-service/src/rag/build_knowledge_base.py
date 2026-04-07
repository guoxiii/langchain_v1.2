# src/rag/build_knowledge_base.py
"""
建構 FAQ 知識庫的 RAG 管線。
將 FAQ 文件切割、嵌入、存入 Chroma 向量資料庫。
"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# 匯入 FAQ 資料
from src.rag.prepare_faq import FAQ_DOCUMENTS

# 定義持久化路徑
CHROMA_PERSIST_DIR = "./data/chroma_faq_db"
COLLECTION_NAME = "customer_service_faq"

def build_knowledge_base():
    """建構 FAQ 知識庫。"""
    # Step 1: 將 FAQ 轉換為 LangChain Document 格式
    documents = []

    for faq in FAQ_DOCUMENTS:
        # 把問題和答案組合成一個完整的文件
        content = f"問題：{faq['question']}\n\n答案：{faq['answer'].strip()}"
        doc = Document(
            page_content=content,
            metadata={
                "category": faq["category"],
                "question": faq["question"],
                "source": "FAQ 知識庫",
            },
        )

        documents.append(doc)

    print(f"✅ 載入 {len(documents)} 份 FAQ 文件")

    # Step 2: 文字切割
    # FAQ 通常不會太長，但為了保持一致性，我們還是進行切割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "，", " "],
    )

    splits = text_splitter.split_documents(documents)
    print(f"✅ 切割為 {len(splits)} 個文字區塊")

    # Step 3: 嵌入 + 存入向量資料庫
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )

    print(f"✅ 向量資料庫建構完成，存於 {CHROMA_PERSIST_DIR}")
    return vectorstore

def load_knowledge_base():
    """載入已建構的 FAQ 知識庫。"""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )

    return vectorstore

if __name__ == "__main__":
    build_knowledge_base()
