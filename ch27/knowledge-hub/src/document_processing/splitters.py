# src/document_processing/splitters.py
"""文字切割器 — 把大象切成可消化的小塊"""

from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import config

class KnowledgeHubSplitter:
    """
    企業知識庫專用的文字切割器

    特點：
    1. 保留文件的結構化資訊（標題、段落）
    2. 為每個 chunk 添加上下文 metadata
    3. 針對中文內容最佳化分隔符
    """

    def __init__(
        self,
        chunk_size: int = config.chunk_size,
        chunk_overlap: int = config.chunk_overlap,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",    # 段落分隔（最優先）
                "\n",      # 換行
                "。",      # 中文句號
                "！",      # 中文驚嘆號
                "？",      # 中文問號
                "；",      # 中文分號
                ". ",      # 英文句號
                ", ",      # 英文逗號
                " ",       # 空格
                "",        # 最後手段：逐字切割
            ],
            length_function=len,
        )

    def split_with_context(
        self, documents: list[Document]
    ) -> list[Document]:
        """
        切割文件並為每個 chunk 添加上下文資訊

        每個 chunk 的 metadata 會包含：
        - chunk_index: 該 chunk 在原始文件中的順序
        - total_chunks: 該文件的總 chunk 數
        - doc_id: 來源文件 ID（方便回溯）
        """

        all_chunks = []

        for doc in documents:
            # 切割單一文件
            chunks = self.splitter.split_documents([doc])

            # 添加 chunk 上下文
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)

            all_chunks.extend(chunks)

        return all_chunks
