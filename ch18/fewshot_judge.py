# fewshot_judge.py

from dotenv import load_dotenv
load_dotenv()

from openevals.llm import create_llm_as_judge

# ============================================================
# 帶有 few-shot 範例的評審 Prompt
# ============================================================

TECHNICAL_ACCURACY_PROMPT = """你是一位 LangChain 技術書籍的審稿員。
請評估以下技術回答的準確性。
使用者問題：{inputs}
AI 回答：{outputs}
參考答案：{reference_outputs}

請判斷 AI 回答是否技術上準確。回覆 True 或 False。
"""

# Few-shot 範例：教導評審什麼算正確、什麼算錯誤
few_shot_examples = [
    {
        "inputs": "LangChain v1 使用什麼取代 LCEL？",
        "outputs": "LangChain v1 使用 create_agent 和 Middleware 系統取代 LCEL。",
        "reference_outputs": "v1 淘汰 LCEL，改用 create_agent + Middleware。",
        "score": True,
        "comment": "技術上準確。正確指出 create_agent 和 Middleware 是 LCEL 的替代方案。",
    },
    {
        "inputs": "LangChain v1 的最低 Python 版本要求？",
        "outputs": "LangChain v1 支援 Python 3.8 以上。",
        "reference_outputs": "LangChain v1 要求 Python 3.10+，已停止支援 3.9。",
        "score": False,
        "comment": "技術上不準確。v1 最低要求 Python 3.10，而非 3.8。版本要求是重要的相容性資訊，不能搞錯。",
    },
]

tech_evaluator = create_llm_as_judge(
    prompt=TECHNICAL_ACCURACY_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="technical_accuracy",
    few_shot_examples=few_shot_examples,
)

# 測試
result = tech_evaluator(
    inputs="deepagents 套件的用途是什麼？",
    outputs="deepagents 是 LangChain 的內建模組，用於建立簡單的聊天機器人。",
    reference_outputs="deepagents 是獨立套件，用於建立具備規劃、檔案系統、子 Agent 能力的深度 Agent。",
)

print(f"技術準確性：{result['score']}")
print(f"評語：{result['comment']}")
