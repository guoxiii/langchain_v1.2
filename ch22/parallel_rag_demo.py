"""
檔案：parallel_rag_demo.py
並行 RAG 檢索：同時從多個來源搜尋
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from langchain.embeddings import init_embeddings
from langchain_core.vectorstores import InMemoryVectorStore


async def parallel_retrieval(
    query: str,
    retrievers: list,
) -> list:
    """同時從多個 Retriever 搜尋，合併結果"""
    tasks = [
        retriever.ainvoke(query)
        for retriever in retrievers
    ]

    # asyncio.gather 會同時執行所有搜尋
    results = await asyncio.gather(*tasks)

    # 合併所有結果並去重
    all_docs = []
    seen_contents = set()

    for docs in results:
        for doc in docs:
            if doc.page_content not in seen_contents:
                seen_contents.add(doc.page_content)
                all_docs.append(doc)

    return all_docs

async def main():
    embeddings = init_embeddings("google_genai:gemini-embedding-001")
    # 假設我們有三個不同的 Vector Store（FAQ、技術文件、操作手冊）
    faq_store = InMemoryVectorStore(embeddings)
    tech_store = InMemoryVectorStore(embeddings)
    manual_store = InMemoryVectorStore(embeddings)

    # ... 假設已經載入了文件 ...
    retrievers = [
        faq_store.as_retriever(search_kwargs={"k": 3}),
        tech_store.as_retriever(search_kwargs={"k": 3}),
        manual_store.as_retriever(search_kwargs={"k": 3}),
    ]

    # 並行搜尋三個來源 —— 耗時約等於最慢的那一個，而非三者加總
    docs = await parallel_retrieval("如何重設密碼", retrievers)
    print(f"從三個來源共找到 {len(docs)} 篇相關文件")

asyncio.run(main())
