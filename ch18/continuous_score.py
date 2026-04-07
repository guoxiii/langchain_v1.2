# continuous_score.py

from dotenv import load_dotenv
load_dotenv()

from openevals.llm import create_llm_as_judge

# ============================================================
# 自定義 Prompt，使用連續分數（0-1）
# ============================================================

FAITHFULNESS_PROMPT = """【重要】你的所有回覆（包括 reasoning 和 comment）都必須使用繁體中文。

你是一個 RAG 系統的品質審查員。
請評估以下 AI 回答的「忠實度」(Faithfulness)：

回答是否忠實地基於提供的上下文？是否有虛構不存在於上下文中的資訊？
使用者問題：{inputs}
AI 回答：{outputs}
參考上下文：{reference_outputs}

請給出 0 到 1 之間的分數：
- 1.0：完全忠實於上下文，沒有虛構
- 0.7-0.9：大部分忠實，有少量推論但合理
- 0.4-0.6：部分忠實，有些內容超出上下文範圍
- 0.1-0.3：大量虛構，與上下文不符
- 0.0：完全虛構

請以 JSON 格式回覆：
{{"score": <float>, "comment": "<繁體中文說明>"}}
"""

faithfulness_evaluator = create_llm_as_judge(
    prompt=FAITHFULNESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="faithfulness",
    continuous=True,  # ← 加這行，分數就會是 0.0~1.0 的數字
)

# 測試
result = faithfulness_evaluator(
    inputs="台灣的首都在哪裡？",
    outputs="台灣的首都是台北市，位於台灣北部。台北是一個現代化的城市，人口約 260 萬。",
    reference_outputs="台灣的行政中心是台北市。",
)

print(f"忠實度分數：{result['score']}")
print(f"評語：{result['comment']}")
