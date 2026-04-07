# src/models.py
"""KnowledgeHub 資料模型"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class DocumentStatus(str, Enum):
    """文件狀態枚舉"""
    PENDING = "pending"          # 待審核
    PROCESSING = "processing"    # 處理中
    INDEXED = "indexed"          # 已索引
    REJECTED = "rejected"        # 已拒絕
    ARCHIVED = "archived"        # 已歸檔

class UserRole(str, Enum):
    """使用者角色"""
    ADMIN = "admin"              # 管理員：可管理所有文件
    EDITOR = "editor"            # 編輯者：可上傳與編輯文件
    VIEWER = "viewer"            # 檢視者：僅可查詢

class DocumentMetadata(BaseModel):
    """文件 Metadata — 每份文件的身分證"""
    doc_id: str = Field(description="文件唯一識別碼")
    title: str = Field(description="文件標題")
    file_type: str = Field(description="檔案類型：pdf, docx, md, txt")
    file_path: str = Field(description="原始檔案路徑")
    file_size_bytes: int = Field(description="檔案大小（位元組）")

    # 文件狀態
    status: DocumentStatus = DocumentStatus.PENDING
    uploaded_by: str = Field(description="上傳者 ID")
    uploaded_at: datetime = Field(default_factory=datetime.now)
    reviewed_by: Optional[str] = Field(default=None, description="審核者 ID")
    reviewed_at: Optional[datetime] = None

    # 內容摘要
    summary: Optional[str] = Field(default=None, description="AI 自動產生的摘要")
    chunk_count: int = Field(default=0, description="切割後的 chunk 數量")
    tags: list[str] = Field(default_factory=list, description="文件標籤")

    # 權限
    access_roles: list[UserRole] = Field(
        default_factory=lambda: [UserRole.ADMIN, UserRole.EDITOR, UserRole.VIEWER],
        description="可存取的角色列表"
    )


class QueryRecord(BaseModel):
    """查詢紀錄 — 用於使用統計"""
    query_id: str
    user_id: str
    question: str
    answer: str
    sources: list[str] = Field(default_factory=list, description="引用的文件 ID")
    feedback: Optional[str] = None   # "helpful" | "not_helpful"
    created_at: datetime = Field(default_factory=datetime.now)
