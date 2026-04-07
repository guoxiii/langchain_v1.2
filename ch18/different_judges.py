# different_judges.py

from dotenv import load_dotenv
load_dotenv()

from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# ============================================================
# 使用不同模型作為評審
# ============================================================

# 方案 A：使用 Gemini
gemini_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="correctness_gemini",
)

# 方案 B：使用 Claude 作為評審
claude_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="anthropic:claude-sonnet-4-6",
    feedback_key="correctness_claude",
)

# ============================================================
# 同一個案例，讓兩位評審分別打分
# ============================================================
test_case = {
    "inputs": "什麼是 LCEL？",
    "outputs": "LCEL 是 LangChain Expression Language，它是 LangChain 舊版的管道語法。"
               "在 LangChain v1 中，LCEL 已經移至 langchain-classic 套件。",
    "reference_outputs": "LCEL（LangChain Expression Language）是 LangChain v0.x 的管道操作語法，在 v1 中，相關功能移至 langchain-classic。"
}

result_gemini = gemini_judge(**test_case)
result_claude = claude_judge(**test_case)

print(f"🤖 Gemini 評審：score={result_gemini['score']}")
print(f"   評語：{result_gemini['comment'][:100]}...")
print()
print(f"🤖 Claude 評審：score={result_claude['score']}")
print(f"   評語：{result_claude['comment'][:100]}...")
