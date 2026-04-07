# incremental_update.py

"""增量更新模組 — 只更新有變動的文件"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from src.document_pipeline import DocumentPipeline, compute_doc_hash
from src.vector_store import VectorStoreManager
from src.knowledge_graph import KnowledgeGraphBuilder

class IncrementalUpdater:
    """
    增量更新管理器。
    工作原理：
    1. 計算新文件的 content hash
    2. 與現有索引中的 hash 比對
    3. 只處理新增或有變動的文件
    4. 同時更新向量存儲和知識圖譜

    就像快遞配送中心：
    - 新包裹進來 → 入庫（新增）
    - 舊包裹換了內容 → 替換（更新）
    - 包裹被取消 → 移出倉庫（刪除）
    """
    def __init__(self):
        self.pipeline = DocumentPipeline()
        self.vector_store = VectorStoreManager()
        self.kg_builder = KnowledgeGraphBuilder()

    def get_existing_hashes(self) -> set[str]:
        """
        取得目前向量存儲中所有文件的 hash。
        這裡使用 Chroma 的 get() 方法來取得所有 metadata。
        """

        try:
            collection = self.vector_store.vectorstore._collection
            result = collection.get(include=["metadatas"])
            hashes = set()

            if result and result["metadatas"]:
                for meta in result["metadatas"]:
                    if meta and "doc_hash" in meta:
                        hashes.add(meta["doc_hash"])

            return hashes
        except Exception as e:
            print(f"⚠️ 取得現有 hash 失敗：{e}")
            return set()

    def update(self, sources: list[dict]) -> dict:
        """
        執行增量更新。

        Args:
            sources: 文件來源列表（同 DocumentPipeline.process 格式）

        Returns:
            更新統計資訊
        """

        print("🔄 開始增量更新...\n")

        # Step 1: 取得現有的 hash
        existing_hashes = self.get_existing_hashes()
        print(f"📦 目前索引中有 {len(existing_hashes)} 個唯一 hash\n")

        # Step 2: 處理新文件
        all_chunks = self.pipeline.process(sources)

        # Step 3: 比對 hash，找出需要更新的 chunks
        new_chunks: list[Document] = []
        skipped = 0

        for chunk in all_chunks:
            chunk_hash = chunk.metadata.get("doc_hash", "")

            if chunk_hash in existing_hashes:
                skipped += 1
            else:
                new_chunks.append(chunk)

        print(f"\n📊 比對結果：")
        print(f"   跳過（未變動）：{skipped} 個 chunks")
        print(f"   新增/更新：{len(new_chunks)} 個 chunks")

        if not new_chunks:
            print("\n✅ 沒有需要更新的文件！")

            return {
                "total_processed": len(all_chunks),
                "skipped": skipped,
                "new_or_updated": 0,
            }

        # Step 4: 更新向量存儲
        print(f"\n📥 更新向量存儲...")
        self.vector_store.add_documents(new_chunks)

        # Step 5: 更新知識圖譜
        print(f"\n📥 更新知識圖譜...")
        self.kg_builder.build_from_documents(new_chunks)

        stats = {
            "total_processed": len(all_chunks),
            "skipped": skipped,
            "new_or_updated": len(new_chunks),
        }

        print(f"\n✅ 增量更新完成！")
        return stats

if __name__ == "__main__":
    updater = IncrementalUpdater()

    # 第一次：全量建索引
    print("=" * 60)
    print("第一次執行（全量建索引）")
    print("=" * 60)

    updater.update([
        {

            "source": "docs/employee_handbook.pdf",
            "department": "hr",
            "access_level": "internal",
        },
    ])

    # 第二次：同樣的文件不會重複建索引
    print("\n" + "=" * 60)
    print("第二次執行（應該全部跳過）")
    print("=" * 60)

    updater.update([
        {
            "source": "docs/employee_handbook.pdf",
            "department": "hr",
            "access_level": "internal",
        },
    ])
