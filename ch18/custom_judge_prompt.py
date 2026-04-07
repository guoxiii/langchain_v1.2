# custom_judge_prompt.py

from dotenv import load_dotenv
load_dotenv()

from openevals.llm import create_llm_as_judge

# ============================================================
# 為 RAG 系統設計的多維度評估 Prompt
# ============================================================

RAG_EVALUATION_PROMPT = """你是一位嚴謹的 RAG（檢索增強生成）系統品質審查員。
請根據以下維度評估 AI 回答的品質：
## 輸入資訊
- 使用者問題：{inputs}
- AI 回答：{outputs}
- 參考答案：{reference_outputs}

## 評估維度
1. **事實正確性**（最重要）：
   - 回答中的事實是否正確？
   - 是否存在與參考答案矛盾的內容？
2. **完整性**：
   - 回答是否涵蓋了問題的所有面向？
   - 是否遺漏了重要資訊？
3. **簡潔性**：
   - 回答是否簡明扼要？
   - 是否有不必要的冗長說明？

## 評分標準
- 1.0：在所有維度上都表現優秀
- 0.8：大致正確且完整，但有小瑕疵
- 0.6：基本正確但有明顯遺漏或小錯誤
- 0.4：部分正確但有較大問題
- 0.2：大部分不正確或嚴重不完整
- 0.0：完全錯誤或不相關

請以 JSON 格式回覆你的評估結果：
{{"score": <float>, "comment": "<包含各維度分析的詳細評語>"}}
"""

rag_evaluator = create_llm_as_judge(
    prompt=RAG_EVALUATION_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="rag_quality",
    continuous=True,
)

# 測試案例
result = rag_evaluator(
    inputs="LangChain v1 的 Middleware 系統有哪些內建 Middleware？",
    outputs=(
        "LangChain v1 內建了以下 Middleware：\n"
        "1. HumanInTheLoopMiddleware - 人工審核\n"
        "2. SummarizationMiddleware - 對話摘要\n"
        "3. PIIMiddleware - 敏感資訊遮蔽\n"
        "這三個是最常用的內建 Middleware。"
    ),

    reference_outputs=(
        "LangChain v1 提供五種內建 Middleware：\n"
        "1. HumanInTheLoopMiddleware - 工具呼叫審核\n"
        "2. SummarizationMiddleware - 對話歷史摘要\n"
        "3. PIIMiddleware - 敏感資訊遮蔽\n"
        "4. ContentModerationMiddleware (v1.1+) - 內容安全過濾\n"
        "5. ModelRetryMiddleware (v1.1+) - 指數退避重試"
    ),
)

print(f"📊 RAG 品質評分：{result['score']}")
print(f"📝 詳細評語：\n{result['comment']}")
