# experiment_comparison.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from langchain.chat_models import init_chat_model
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

ls_client = Client()

correctness_eval = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="correctness",
)

# ============================================================
# 版本 A：使用基礎 System Prompt
# ============================================================

model_a = init_chat_model("google_genai:gemini-2.5-flash")

def agent_baseline(inputs: dict) -> dict:
    response = model_a.invoke([
        {"role": "system", "content": "回答使用者的技術問題。"},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.content}

results_a = ls_client.evaluate(
    agent_baseline,
    data="RAG-QA-Evaluation-v1",
    evaluators=[correctness_eval],
    experiment_prefix="Baseline-Simple-Prompt",
    description="基準版本：簡單 System Prompt",
)

print("✅ 基準版本 Experiment 完成")

# ============================================================
# 版本 B：使用最佳化的 System Prompt
# ============================================================

def agent_optimized(inputs: dict) -> dict:
    optimized_prompt = (
        "你是一位 LangChain v1 技術專家。回答規範：\n"
        "1. 使用繁體中文回答，專有名詞保留英文\n"
        "2. 先給出簡潔的一句話摘要，再提供詳細說明\n"
        "3. 提及具體的 API 名稱、模組路徑和版本號\n"
        "4. 如果有相關的注意事項或常見陷阱，請一併說明\n"
    )

    response = model_a.invoke([
        {"role": "system", "content": optimized_prompt},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.content}

results_b = ls_client.evaluate(
    agent_optimized,
    data="RAG-QA-Evaluation-v1",
    evaluators=[correctness_eval],
    experiment_prefix="Optimized-Detailed-Prompt",
    description="最佳化版本：結構化 System Prompt",
)

print("✅ 最佳化版本 Experiment 完成")

# ============================================================
# 提示使用者去 Dashboard 比較
# ============================================================

print("\n📊 兩組 Experiment 已完成！")
print("前往 LangSmith Dashboard → Datasets → RAG-QA-Evaluation-v1")
print("選取兩個 Experiment，點擊 Compare 查看並排比較結果")
