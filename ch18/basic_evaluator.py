# basic_evaluator.py

from dotenv import load_dotenv
load_dotenv()

from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# ============================================================
# 建立一個正確性評估器
# ============================================================

correctness_evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT + "\n\nIMPORTANT: 用繁體中文撰寫回饋/評論",
    model="google_genai:gemini-2.5-flash",
    feedback_key="correctness",              # 回饋的鍵名
)

# ============================================================
# 模擬一個評估場景
# ============================================================

# 使用者問題
inputs = "LangChain v1 的 create_agent 函式是做什麼的？"
# Agent 的實際輸出（假設你的 Agent 回答了這個）
outputs = (
    "create_agent 是 LangChain v1 中用來建立 AI Agent 的核心函式。"
    "它底層使用 LangGraph 的 StateGraph，回傳 CompiledStateGraph 物件。"
    "此函式取代了舊版的 create_react_agent。"
)

# 標準答案（你期望的回答）
reference_outputs = (
    "create_agent 是 LangChain v1 的核心函式，來自 langchain.agents 模組。"
    "它用於建立 AI Agent，底層使用 LangGraph runtime。"
    "回傳值為 CompiledStateGraph，取代了已棄用的 create_react_agent。"
)

# ============================================================
# 執行評估
# ============================================================

result = correctness_evaluator(
    inputs=inputs,
    outputs=outputs,
    reference_outputs=reference_outputs,
)

print(f"📊 評估結果：")
print(f"   指標：{result['key']}")
print(f"   分數：{result['score']}")
print(f"   評語：{result['comment']}")
