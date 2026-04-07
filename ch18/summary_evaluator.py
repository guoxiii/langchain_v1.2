# summary_evaluator.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
ls_client = Client()

# ============================================================
# Summary Evaluator：計算整體準確率
# ============================================================

def overall_accuracy(
    outputs: list[dict],
    reference_outputs: list[dict],
) -> dict:
    """計算所有案例中，回答長度在合理範圍內的比例"""
    total = len(outputs)

    if total == 0:
        return {"key": "overall_length_pass_rate", "score": 0.0,
                "comment": "無資料"}

    passed = sum(
        1 for out in outputs
        if 50 <= len(str(out.get("answer", ""))) <= 500
    )

    rate = passed / total

    return {
        "key": "overall_length_pass_rate",
        "score": round(rate, 2),
        "comment": f"通過率 {rate:.0%} ({passed}/{total} 個案例長度合格)"
    }

# 在 evaluate 中使用 summary_evaluators
# results = ls_client.evaluate(
#     my_agent,
#     data="RAG-QA-Evaluation-v1",
#     evaluators=[...],
#     summary_evaluators=[overall_accuracy],
#     experiment_prefix="With-Summary",
# )
