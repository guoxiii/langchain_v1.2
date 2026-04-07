# ch06/pydantic_schema_guide.py

"""Pydantic Model 定義 Schema 的完整指南"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# ========== 1. 基本欄位型別 ==========
class BasicExample(BaseModel):
    """基本欄位型別示範"""
    name: str = Field(description="名稱")
    age: int = Field(description="年齡")
    score: float = Field(description="分數")
    is_active: bool = Field(description="是否啟用")

# ========== 2. 列表與巢狀結構 ==========
class Address(BaseModel):
    """地址"""
    city: str = Field(description="城市")
    district: str = Field(description="區域")
    street: str = Field(description="街道地址")

class Employee(BaseModel):
    """員工資訊 — 示範巢狀結構"""
    name: str = Field(description="員工姓名")
    department: str = Field(description="所屬部門")
    skills: list[str] = Field(description="技能列表")
    address: Address = Field(description="居住地址")  # 巢狀 Model

# ========== 3. 使用 Enum 限制選項 ==========
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SentimentAnalysis(BaseModel):
    """情緒分析結果 — 示範 Enum 限制選項"""
    sentiment: Sentiment = Field(description="情緒類型")
    confidence: float = Field(description="信心分數（0.0 到 1.0）")
    reasoning: str = Field(description="判斷理由")

# ========== 4. 選填欄位 ==========
class ProductReview(BaseModel):
    """產品評論 — 示範選填欄位"""
    product_name: str = Field(description="產品名稱")
    rating: int = Field(description="評分（1-5 星）")
    review_text: str = Field(description="評論內容")
    pros: list[str] = Field(description="優點列表")
    cons: list[str] = Field(description="缺點列表")
    purchase_date: Optional[str] = Field(
        default=None,
        description="購買日期（如果有提到的話）"
    )

# ========== 5. 加入欄位驗證 ==========
class ExamScore(BaseModel):
    """考試成績 — 示範欄位驗證"""
    student_name: str = Field(description="學生姓名")
    subject: str = Field(description="科目名稱")
    score: int = Field(
        description="考試分數",
        ge=0,    # >= 0（greater than or equal）
        le=100,  # <= 100（less than or equal）
    )

    grade: str = Field(
        description="等級（A/B/C/D/F）",
        pattern=r"^[ABCDF]$",  # 正則表達式驗證
    )
