# src/indexing/incremental.py
"""增量索引管線 — 新文件自動上架的流水線"""

from dotenv import load_dotenv
load_dotenv()

import json
from pathlib import Path
from datetime import datetime
from src.models import DocumentMetadata, DocumentStatus
from src.document_processing.loaders import MultiFormatLoader
from src.document_processing.splitters import KnowledgeHubSplitter
from src.document_processing.summarizer import DocumentSummarizer
from src.indexing.vector_index import VectorIndexManager
from src.indexing.graph_index import GraphIndexManager

class IncrementalIndexPipeline:
    """
    增量索引管線

    工作流程：
    1. 載入文件 → 2. 切割 → 3. 摘要 → 4. 向量索引 → 5. 圖譜索引 → 6. 更新狀態

    增量策略：
    - 維護一個 metadata JSON 檔案，記錄已處理的文件
    - 只處理新增或修改的文件
    - 支援文件更新（先刪除舊索引，再建立新索引）
    """

    def __init__(self):
        self.loader = MultiFormatLoader()
        self.splitter = KnowledgeHubSplitter()
        self.summarizer = DocumentSummarizer()
        self.vector_index = VectorIndexManager()
        self.graph_index = GraphIndexManager()

        # Metadata 儲存路徑
        self.metadata_path = Path("./data/metadata.json")
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self._metadata_store: dict[str, dict] = self._load_metadata()

    def _load_metadata(self) -> dict[str, dict]:
        """載入已處理文件的 metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)

        return {}

    def _save_metadata(self) -> None:
        """儲存 metadata"""
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self._metadata_store, f, ensure_ascii=False, indent=2, default=str)

    async def process_file(
        self,
        file_path: str,
        uploaded_by: str = "system",
        tags: list[str] | None = None,
        build_graph: bool = True,
    ) -> DocumentMetadata:
        """
        處理單一文件的完整管線

        Parameters
        ----------

        file_path : str
            檔案路徑

        uploaded_by : str
            上傳者 ID

        tags : list[str] | None
            文件標籤

        build_graph : bool
            是否建立知識圖譜（可選，因為圖譜建構較耗時）

        Returns
        -------

        DocumentMetadata
            處理完成的文件 metadata
        """

        print(f"\n{'='*60}")
        print(f"📄 開始處理：{file_path}")
        print(f"{'='*60}")

        # Step 1: 載入文件
        print("📖 Step 1/5：載入文件...")

        documents, metadata = self.loader.load_file(
            file_path, uploaded_by=uploaded_by, tags=tags
        )

        # 檢查是否需要更新（增量檢查）
        if metadata.doc_id in self._metadata_store:
            existing = self._metadata_store[metadata.doc_id]
            if existing.get("file_size_bytes") == metadata.file_size_bytes:
                print("⏭️ 文件未變更，跳過處理")
                return DocumentMetadata(**existing)
            else:
                print("🔄 文件已更新，重新索引...")
                self.vector_index.delete_document(metadata.doc_id)

                if build_graph:
                    self.graph_index.delete_document_nodes(metadata.doc_id)

        # Step 2: 文字切割
        print("✂️ Step 2/5：切割文字...")
        chunks = self.splitter.split_with_context(documents)
        metadata.chunk_count = len(chunks)
        print(f"   產生 {len(chunks)} 個 chunks")

        # Step 3: AI 摘要
        print("🤖 Step 3/5：產生 AI 摘要...")
        metadata.summary = await self.summarizer.summarize(documents)
        print(f"   摘要：{metadata.summary[:80]}...")

        # Step 4: 向量索引
        print("📊 Step 4/5：建立向量索引...")
        self.vector_index.add_documents(chunks, metadata.doc_id)

        # Step 5: 知識圖譜（可選）
        if build_graph:
            print("🔗 Step 5/5：建立知識圖譜...")
            await self.graph_index.add_to_graph(chunks[:10], metadata.doc_id)
            # 注意：只取前 10 個 chunks 做圖譜提取，避免 API 成本過高
        else:
            print("⏭️ Step 5/5：跳過知識圖譜建構")

        # 更新狀態
        metadata.status = DocumentStatus.INDEXED
        self._metadata_store[metadata.doc_id] = metadata.model_dump()
        self._save_metadata()
        print(f"\n✅ 處理完成！doc_id: {metadata.doc_id}")
        return metadata

    async def process_directory(
        self,
        directory: str,
        uploaded_by: str = "system",
        build_graph: bool = True,
    ) -> list[DocumentMetadata]:
        """批次處理整個目錄"""
        results = []
        dir_path = Path(directory)

        for file_path in sorted(dir_path.iterdir()):
            suffix = file_path.suffix.lower()
            if suffix in MultiFormatLoader.LOADER_MAP:
                try:
                    metadata = await self.process_file(
                        str(file_path),
                        uploaded_by=uploaded_by,
                        build_graph=build_graph,
                    )

                    results.append(metadata)
                except Exception as e:
                    print(f"❌ 處理失敗：{file_path.name} — {e}")

        print(f"\n📊 批次處理完成：成功 {len(results)} 份文件")

        return results

    def get_all_metadata(self) -> list[DocumentMetadata]:
        """取得所有已索引文件的 metadata"""
        return [
            DocumentMetadata(**data)
            for data in self._metadata_store.values()
        ]
