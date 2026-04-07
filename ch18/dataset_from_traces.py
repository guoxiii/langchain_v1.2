# dataset_from_traces.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

ls_client = Client()

# 從指定專案中讀取最近的 Trace
runs = ls_client.list_runs(
    project_name="ch18-evaluation-practice",	# 這裡要修改成自己的專案名稱
    execution_order=1,  # 只取頂層 Run
    limit=50,
)

# 篩選出有代表性的案例（例如，使用者有提供反饋的）
interesting_runs = []

for run in runs:
    # 挑選有使用者 feedback 的 Run
    if run.feedback_stats:
        interesting_runs.append(run)

print(f"🔍 找到 {len(interesting_runs)} 個有反饋的 Run")

# 將這些 Run 加入 Dataset
if interesting_runs:
    dataset = ls_client.create_dataset(
        dataset_name="Production-Interesting-Cases",
        description="從生產環境中挑選的有趣案例"
    )

    for run in interesting_runs[:20]:  # 取前 20 個
        ls_client.create_example(
            inputs=run.inputs,
            outputs=run.outputs,  # 使用實際輸出作為參考
            dataset_id=dataset.id,
        )

    print(f"✅ 已從生產 Trace 匯入 {min(len(interesting_runs), 20)} 個案例")
