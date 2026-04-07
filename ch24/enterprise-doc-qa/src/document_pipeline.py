# src/document_pipeline.py

"""多格式文件統一處理管線"""

from dotenv import load_dotenv
load_dotenv()

import hashlib
from datetime import datetime
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    WebBaseLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL

def compute_doc_hash(content: str) -> str:
    """計算文件內容的 hash，用於增量更新判斷。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

class UnifiedDocumentLoader:
    """
    統一文件載入器 — 支援 PDF、Word、網頁。    
    把它想像成一位多語言翻譯員：不管你丟什麼格式的文件，
    它都能翻譯成 LangChain 看得懂的 Document 格式。
    """

    # 檔案類型對應的 Loader 映射表
    LOADER_MAP = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
    }

    def load_file(
        self,
        file_path: str,
        department: str = "general",
        access_level: str = "public",
    ) -> list[Document]:
        """
        載入本地檔案（PDF 或 Word），並附加 metadata。

        Args:
            file_path: 檔案路徑
            department: 所屬部門（用於權限控制）
            access_level: 存取級別 — "public", "internal", "confidential"

        Returns:
            包含 metadata 的 Document 列表
        """

        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in self.LOADER_MAP:
            raise ValueError(
                f"不支援的檔案格式：{suffix}。"
                f"目前支援：{list(self.LOADER_MAP.keys())}"
            )

        loader_class = self.LOADER_MAP[suffix]
        loader = loader_class(str(path))
        documents = loader.load()

        # 為每份文件附加 metadata
        for doc in documents:
            doc.metadata.update({
                "source_type": suffix.lstrip("."),
                "source_path": str(path),
                "file_name": path.name,
                "department": department,
                "access_level": access_level,
                "doc_hash": compute_doc_hash(doc.page_content),
                "indexed_at": datetime.now().isoformat(),
            })

        return documents

    def load_url(
        self,
        url: str,
        department: str = "general",
        access_level: str = "public",
    ) -> list[Document]:
        """
        載入網頁內容。

        Args:
            url: 網頁 URL
            department: 所屬部門
            access_level: 存取級別

        Returns:
            包含 metadata 的 Document 列表
        """

        loader = WebBaseLoader(url)
        documents = loader.load()

        for doc in documents:
            doc.metadata.update({
                "source_type": "web",
                "source_url": url,
                "department": department,
                "access_level": access_level,
                "doc_hash": compute_doc_hash(doc.page_content),
                "indexed_at": datetime.now().isoformat(),
            })

        return documents

    def load_auto(
        self,
        source: str,

        department: str = "general",
        access_level: str = "public",
    ) -> list[Document]:
        """
        自動判斷來源類型並載入。
        如果 source 以 http 開頭，視為網頁；否則視為本地檔案。
        """

        if source.startswith("http://") or source.startswith("https://"):
            return self.load_url(source, department, access_level)
        else:
            return self.load_file(source, department, access_level)

class DocumentChunker:
    """
    文件切割器 — 把長文件切成適合 RAG 的小段落。
    使用 RecursiveCharacterTextSplitter，
    它會優先在段落邊界切割，盡量保持語義完整性。
    """
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
            length_function=len,
        )

    def split_documents(
        self, documents: list[Document]
    ) -> list[Document]:
        """
        切割文件，並為每個 chunk 補充 metadata。
        每個 chunk 會新增：
        - chunk_index: 在原文件中的序號
        - total_chunks: 原文件被切成幾段
        """
        chunks = self.splitter.split_documents(documents)

        # 按原始來源分組，補充 chunk 索引
        source_groups: dict[str, list[Document]] = {}

        for chunk in chunks:
            source = chunk.metadata.get(
                "source_path",
                chunk.metadata.get("source_url", "unknown"),
            )

            source_groups.setdefault(source, []).append(chunk)

        for source, group in source_groups.items():
            for i, chunk in enumerate(group):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(group)

        return chunks

class DocumentPipeline:
    """
    文件處理管線 — 一站式服務。  
    從載入到切割，一氣呵成。
    就像壽司師傅的工作台：
    魚進去（原始文件），壽司出來（切好的 chunks）。
    """
    def __init__(self):
        self.loader = UnifiedDocumentLoader()
        self.chunker = DocumentChunker()

    def process(
        self,
        sources: list[dict],
    ) -> list[Document]:
        """
        批次處理多個文件來源。

        Args:
            sources: 文件來源列表，每項包含：
                - source: 檔案路徑或 URL
                - department: 所屬部門（選填，預設 "general"）
                - access_level: 存取級別（選填，預設 "public"）

        Returns:
            切割後的 Document 列表

        Example:
            >>> pipeline = DocumentPipeline()
            >>> chunks = pipeline.process([
            ...     {
            ...         "source": "docs/員工手冊.pdf",
            ...         "department": "hr",
            ...         "access_level": "internal",
            ...     },
            ...     {
            ...         "source": "docs/產品規格書.docx",
            ...         "department": "engineering",
            ...         "access_level": "confidential",
            ...     },
            ...     {

            ...         "source": "https://company.com/blog/latest",
            ...         "department": "marketing",
            ...         "access_level": "public",
            ...     },
            ... ])
        """

        all_documents: list[Document] = []

        for item in sources:
            source = item["source"]
            department = item.get("department", "general")
            access_level = item.get("access_level", "public")
            print(f"📄 載入文件：{source}")

            try:
                docs = self.loader.load_auto(
                    source, department, access_level
                )

                all_documents.extend(docs)
                print(f"   ✅ 成功載入 {len(docs)} 頁/段")
            except Exception as e:
                print(f"   ❌ 載入失敗：{e}")

        print(f"\n🔪 開始切割 {len(all_documents)} 份文件...")
        chunks = self.chunker.split_documents(all_documents)
        print(f"   ✅ 切割完成，共 {len(chunks)} 個 chunks")
        return chunks

