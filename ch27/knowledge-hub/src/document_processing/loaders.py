# src/document_processing/loaders.py
"""多格式文件載入器 — 企業知識庫的前門警衛"""

from dotenv import load_dotenv
load_dotenv()

import os
import hashlib
from datetime import datetime
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_core.documents import Document
from src.models import DocumentMetadata, DocumentStatus

class MultiFormatLoader:
    """
    多格式文件載入器
    支援 PDF、Word、Markdown、純文字格式。
    就像一個多語翻譯官，不管你拿什麼格式的文件來，
    它都能幫你翻譯成 LangChain 的 Document 格式。
    """

    # 檔案類型與對應的 Loader
    LOADER_MAP = {
        ".pdf": PyPDFLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".doc": UnstructuredWordDocumentLoader,
        ".md": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
    }

    def __init__(self, upload_dir: str = "./data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _generate_doc_id(self, file_path: str) -> str:
        """基於檔案路徑和修改時間產生唯一 ID"""
        stat = os.stat(file_path)
        content = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def load_file(
        self,
        file_path: str,
        uploaded_by: str = "system",
        tags: list[str] | None = None,
    ) -> tuple[list[Document], DocumentMetadata]:
        """
        載入單一文件，回傳 (Documents, Metadata)
        Parameters
        ----------
        file_path : str
            檔案路徑

        uploaded_by : str
            上傳者 ID

        tags : list[str] | None
            文件標籤

        Returns
        -------
        tuple[list[Document], DocumentMetadata]
            解析後的 Document 列表與 Metadata
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in self.LOADER_MAP:
            raise ValueError(
                f"不支援的檔案格式：{suffix}。"
                f"支援的格式：{list(self.LOADER_MAP.keys())}"
            )

        # 選擇對應的 Loader
        loader_cls = self.LOADER_MAP[suffix]
        loader = loader_cls(str(path))

        # 載入文件
        documents = loader.load()

        # 產生 Metadata
        doc_id = self._generate_doc_id(str(path))

        metadata = DocumentMetadata(
            doc_id=doc_id,
            title=path.stem,
            file_type=suffix.lstrip("."),
            file_path=str(path),
            file_size_bytes=os.path.getsize(str(path)),
            status=DocumentStatus.PROCESSING,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.now(),
            tags=tags or [],
        )

        # 將自定義 metadata 附加到每個 Document
        for doc in documents:
            doc.metadata.update({
                "doc_id": doc_id,
                "title": metadata.title,
                "file_type": metadata.file_type,
                "uploaded_by": uploaded_by,
            })

        return documents, metadata

    def load_directory(
        self,
        directory: str,
        uploaded_by: str = "system",
    ) -> list[tuple[list[Document], DocumentMetadata]]:
        """批次載入整個目錄的文件"""
        results = []
        dir_path = Path(directory)

        for file_path in dir_path.iterdir():
            if file_path.suffix.lower() in self.LOADER_MAP:
                try:
                    result = self.load_file(
                        str(file_path), uploaded_by=uploaded_by
                    )

                    results.append(result)
                    print(f"✅ 已載入：{file_path.name}")
                except Exception as e:
                    print(f"❌ 載入失敗：{file_path.name} — {e}")

        print(f"\n📊 載入完成：成功 {len(results)} 份文件")
        return results
