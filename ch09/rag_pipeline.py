# rag_pipeline.py
"""
第九章實作練習：建立一個 PDF 文件的 RAG 管線
這個範例展示完整的 RAG 管線：
1. 載入 PDF 文件
2. 切割文字
3. 嵌入向量 & 存入 Vector Store
4. 語義搜尋 + LLM 生成回答
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# ============================================================
# 步驟 1：載入 PDF 文件
# ============================================================

from langchain_community.document_loaders import PyPDFLoader

print("=" * 60)
print("步驟 1：載入 PDF 文件")
print("=" * 60)

loader = PyPDFLoader("./documents/techcorp_handbook.pdf")
raw_docs = loader.load()

print(f"  載入了 {len(raw_docs)} 頁")

for doc in raw_docs:
    print(f"  - 第 {doc.metadata.get('page', '?')} 頁：{len(doc.page_content)} 字元")

# ============================================================
# 步驟 2：切割文字
# ============================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter

print("\n" + "=" * 60)
print("步驟 2：切割文字")
print("=" * 60)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # 每個 chunk 最多 500 字元
    chunk_overlap=100,    # 相鄰 chunk 重疊 100 字元
)

chunks = text_splitter.split_documents(raw_docs)

print(f"  切割後共 {len(chunks)} 個 chunk")

for i, chunk in enumerate(chunks[:3]):  # 只顯示前 3 個
    print(f"\n  --- Chunk {i+1} ({len(chunk.page_content)} 字元) ---")
    print(f"  來源：第 {chunk.metadata.get('page', '?')} 頁")
    print(f"  內容：{chunk.page_content[:100]}...")

# ============================================================
# 步驟 3：嵌入向量 & 存入 Vector Store
# ============================================================

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

print("\n" + "=" * 60)
print("步驟 3：嵌入向量 & 存入 Vector Store")
print("=" * 60)

# 建立 Embedding 模型
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# 建立 InMemoryVectorStore 並存入所有 chunks
# from_documents() 會自動呼叫 embed_documents() 做向量化

vector_store = InMemoryVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
)

print(f"  已將 {len(chunks)} 個 chunk 存入向量資料庫")

# ============================================================
# 步驟 4：語義搜尋
# ============================================================

print("\n" + "=" * 60)
print("步驟 4：語義搜尋測試")
print("=" * 60)

query = "How many days of annual leave do employees get?"

print(f"\n  查詢：{query}")

# similarity_search() 會自動嵌入查詢，然後在向量資料庫中搜尋
results = vector_store.similarity_search(query, k=3)

print(f"\n  找到 {len(results)} 個相關片段：")

for i, result in enumerate(results, 1):
    print(f"\n  --- 結果 #{i} ---")
    print(f"  來源：第 {result.metadata.get('page', '?')} 頁")
    print(f"  內容：{result.page_content[:200]}")

# ============================================================
# 步驟 5：使用 LLM 根據檢索結果生成回答
# ============================================================

from langchain.chat_models import init_chat_model

print("\n" + "=" * 60)
print("步驟 5：LLM 生成回答")
print("=" * 60)
# 初始化 Chat Model
llm = init_chat_model("google_genai:gemini-2.5-flash")

# 組合上下文
context = "\n\n".join([doc.page_content for doc in results])

# 建立 Prompt
prompt = f"""你是一個專業的企業文件問答助理。請根據以下提供的文件內容回答使用者的問題。

如果文件中沒有相關資訊，請誠實告知「文件中沒有提到這個問題的答案」。

=== 參考文件 ===
{context}

=== 使用者問題 ===
{query}

=== 你的回答 ==="""

from langchain_core.messages import HumanMessage

response = llm.invoke([HumanMessage(content=prompt)])

print(f"\n  問題：{query}")
print(f"\n  回答：{response.content}")

# ============================================================
# 步驟 6：多次問答測試
# ============================================================

print("\n" + "=" * 60)
print("步驟 6：多次問答測試")
print("=" * 60)

test_questions = [
    "What is the remote work policy?",
    "How often do I need to change my password?",
    "Tell me about the company's retirement benefits.",
    "What is the education budget?",
]

for question in test_questions:
    # 搜尋
    results = vector_store.similarity_search(question, k=2)
    context = "\n\n".join([doc.page_content for doc in results])    

    # 生成回答
    prompt = f"""根據以下文件內容回答問題。如果文件中沒有相關資訊，請說明。

文件內容：
{context}

問題：{question}

回答："""    

    response = llm.invoke([HumanMessage(content=prompt)])    

    print(f"\n  Q: {question}")
    print(f"  A: {response.content[:200]}...")
    print()
