# 檔案名稱：reranking_with_llm.py
# 功能：使用 LLM 對檢索結果進行重排序
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from pydantic import BaseModel, Field

# === 1. 模擬 Retriever 回傳的結果 ===
retrieved_docs = [
    Document(page_content="Python 的 decorator 本質上是一個高階函式，接受函式作為參數並回傳新函式。"),
    Document(page_content="Python 支援整數、浮點數、字串等基本資料型態。整數沒有大小限制。"),
    Document(page_content="@property 是 Python 內建的 decorator，可以把方法變成屬性存取。常見用途包括資料驗證和計算屬性。"),
    Document(page_content="Python 的 for 迴圈可以搭配 range() 函式使用，也可以直接迭代列表。"),
    Document(page_content="functools.wraps 是撰寫 decorator 時的最佳實踐，它可以保留被裝飾函式的名稱和文件字串。"),
]

query = "如何撰寫 Python decorator？"

# === 2. 定義重排序的結構化輸出 ===
class RelevanceScore(BaseModel):
    """文件與查詢的相關性評估"""
    score: int = Field(description="相關性分數，0-10 分，10 分表示完全相關")
    reason: str = Field(description="簡短說明為什麼給這個分數")

# === 3. 使用 LLM 評分 ===
llm = init_chat_model("google_genai:gemini-2.5-flash")
scorer = llm.with_structured_output(RelevanceScore)
scored_docs = []

for doc in retrieved_docs:
    result = scorer.invoke(
        f"""請評估以下文件與查詢的相關性。

查詢：{query}
文件內容：{doc.page_content}
請給出 0-10 分的相關性評分。"""
    )

    scored_docs.append((doc, result.score, result.reason))

    print(f"  分數：{result.score}/10 | 原因：{result.reason}")
    print(f"  文件：{doc.page_content[:60]}...")
    print()

# === 4. 按分數重排序 ===
scored_docs.sort(key=lambda x: x[1], reverse=True)
print("=== 重排序後的結果 ===\n")

for i, (doc, score, reason) in enumerate(scored_docs, 1):
    print(f"  [{i}] 分數：{score}/10")
    print(f"      {doc.page_content[:80]}...")
    print()
