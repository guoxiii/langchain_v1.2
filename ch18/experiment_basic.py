# experiment_basic.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from langchain.chat_models import init_chat_model
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

ls_client = Client()
model = init_chat_model("google_genai:gemini-2.5-flash")

# ============================================================
# 定義被測試的 Agent
# ============================================================

def my_agent(inputs: dict) -> dict:
    response = model.invoke([
        {"role": "system", "content": "你是 LangChain 技術顧問。請用繁體中文回答。"},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.text}

# ============================================================
# 定義 Evaluator
# ============================================================

correctness_eval = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="correctness",
)

# ============================================================
# 執行 Experiment
# ============================================================

results = ls_client.evaluate(
    my_agent,                               # 被測試的函式
    data="RAG-QA-Evaluation-v1",            # Dataset 名稱
    evaluators=[correctness_eval],          # Evaluator 列表
    experiment_prefix="Gemini-Flash-v1",    # Experiment 名稱前綴
    description="使用 Gemini 2.5 Flash 的基準測試",
    num_repetitions=1,                      # 每題跑幾次（用於測試穩定性）
    max_concurrency=4,                      # 最大並行數
)

# ============================================================
# 在程式中查看結果
# ============================================================
# 注意：ls_client.evaluate() 回傳的每個 item 是 dict，不是物件，
#       要用 result["run"] 這種 key 存取，而不是 result.run。
#       但 dict 裡面的 Run / EvaluationResult 本身又是物件，
#       要用 run.inputs、eval_result.score 這種屬性存取。

for i, result in enumerate(results):
    print(f"\n--- 案例 {i + 1} ---")

    # 外層是 dict：用 .get() 取出 Run 物件
    run = result.get("run")
    if run is not None:
        inputs = run.inputs or {}
        outputs = run.outputs or {}
        question = inputs.get("question", "N/A")
        answer = str(outputs.get("answer", "N/A"))
        print(f"問題：{question[:50]}...")
        print(f"回答：{answer[:80]}...")

    # evaluation_results 也是 dict，裡面的 "results" 才是 EvaluationResult 列表
    eval_results = result.get("evaluation_results")
    if eval_results:
        for eval_result in eval_results.get("results", []):
            # EvaluationResult 是物件，用屬性存取
            print(f"評分：{eval_result.key} = {eval_result.score}")

print("\n✅ 前往 LangSmith Dashboard 查看完整的 Experiment 結果")
print("🔗 https://smith.langchain.com")