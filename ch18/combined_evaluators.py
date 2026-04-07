# combined_evaluators.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT, CONCISENESS_PROMPT

ls_client = Client()

# ============================================================
# 組合多個 Evaluator
# ============================================================

# 1. LLM-as-Judge：正確性
correctness = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="correctness",
)

# 2. LLM-as-Judge：簡潔性
conciseness = create_llm_as_judge(
    prompt=CONCISENESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="conciseness",
)

# 3. 自定義：回答長度
def length_check(inputs: dict, outputs: dict, **kwargs) -> dict:
    answer = str(outputs.get("answer", ""))
    score = 1.0 if 50 <= len(answer) <= 500 else 0.5
    return {"key": "length_appropriate", "score": score,
            "comment": f"回答長度 {len(answer)} 字"}

# 4. 自定義：關鍵詞命中
def keyword_hit(inputs: dict, outputs: dict, reference_outputs: dict, **kwargs) -> dict:
    import re

    ref = str(reference_outputs.get("answer", ""))
    out = str(outputs.get("answer", ""))

    keywords = {kw for kw in re.findall(r'[A-Za-z_]\w{3,}', ref)}

    if not keywords:
        return {"key": "keyword_hit", "score": 1.0, "comment": "N/A"}

    hits = sum(1 for kw in keywords if kw.lower() in out.lower())
    score = hits / len(keywords)

    return {"key": "keyword_hit", "score": round(score, 2),
            "comment": f"{hits}/{len(keywords)} keywords found"}

# ============================================================
# 一次跑四個 Evaluator
# ============================================================

from langchain.chat_models import init_chat_model
model = init_chat_model("google_genai:gemini-2.5-flash")

def my_rag_agent(inputs: dict) -> dict:
    """模擬的 RAG Agent"""
    response = model.invoke([
        {"role": "system", "content": "你是 LangChain 技術助手，請準確回答技術問題。"},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.text}

# 使用 client.evaluate 一次執行所有 Evaluator
experiment_results = ls_client.evaluate(
    my_rag_agent,
    data="RAG-QA-Evaluation-v1",
    evaluators=[correctness, conciseness, length_check, keyword_hit],
    experiment_prefix="Multi-Eval-RAG",
    description="多維度評估：正確性 + 簡潔性 + 長度 + 關鍵詞",
)

print("✅ 多維度評估完成！前往 LangSmith Dashboard 查看結果")
