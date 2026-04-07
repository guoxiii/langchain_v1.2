# annotate_traces.py

"""為 Trace 新增人工標記"""

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()
client = Client()

# 取得最近的 Trace
runs = list(
    client.list_runs(
        project_name="ch17-rag-agent-practice",
        execution_order=1,
        limit=4,
    )
)

# 模擬人工標記
# 在實際情境中，這些評分會由人工審查得出
feedback_scores = {
    "你們週日有開嗎": {"correctness": 1.0, "helpfulness": 1.0},
    "退貨": {"correctness": 1.0, "helpfulness": 0.9},
    "免運費": {"correctness": 1.0, "helpfulness": 1.0},
    "筆電": {"correctness": 0.8, "helpfulness": 0.7},
}

for run in runs:
    run_name = run.name or ""

    for keyword, scores in feedback_scores.items():
        if keyword in run_name:
            for key, score in scores.items():
                client.create_feedback(
                    run_id=run.id,
                    key=key,
                    score=score,
                )

            print(f"✅ 已為 '{run_name}' 新增 Feedback")
            break

print("\n🎉 所有標記完成！前往 LangSmith Dashboard 查看結果。")
