# ch08/pydantic_schema.py
from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Literal

class SearchInput(BaseModel):
    """搜尋商品的輸入參數。"""
    keyword: str = Field(description="搜尋關鍵字")

    category: Literal["electronics", "books", "clothing"] = Field(
        default="electronics",
        description="商品分類，可選：electronics、books、clothing"
    )

    max_results: int = Field(
        default=5,
        description="最多回傳幾筆結果（1-20）",
        ge=1,
        le=20
    )

@tool(args_schema=SearchInput)
def search_products(keyword: str, category: str = "electronics", max_results: int = 5) -> str:
    """搜尋商品目錄中符合條件的商品。"""
    # 模擬搜尋結果
    return f"在 {category} 分類中搜尋「{keyword}」，找到 {max_results} 筆結果"

# 查看產生的 Schema
import json

print(json.dumps(search_products.args, indent=2, ensure_ascii=False))