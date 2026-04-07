# ch17/analyze_traces.py

"""使用 LangSmith SDK 查詢和分析 Trace"""

from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

# 列出專案中最近的 Trace
print("📊 最近的 Trace：")
print("-" * 80)

runs = list(
    client.list_runs(
        project_name="ch17-rag-agent-practice",
        execution_order=1,  # 只取根 Run（即 Trace）
        limit=10,
    )
)

for run in runs:
    status = "✅" if run.status == "success" else "❌"
    latency = (
        f"{(run.end_time - run.start_time).total_seconds():.2f}s"
        if run.end_time
        else "N/A"
    )

    tokens = run.total_tokens or 0

    print(f"  {status} {run.name}")
    print(f"     延遲: {latency} | Token: {tokens}")
    print(f"     Tags: {run.tags}")
    print()

# 統計
print("📈 統計摘要：")
total_tokens = sum(r.total_tokens or 0 for r in runs)

total_latency = sum(
    (r.end_time - r.start_time).total_seconds()
    for r in runs
    if r.end_time
)

success_count = sum(1 for r in runs if r.status == "success")

print(f"  總 Trace 數: {len(runs)}")
print(f"  成功率: {success_count}/{len(runs)}")
print(f"  總 Token 消耗: {total_tokens}")
print(f"  總延遲: {total_latency:.2f}s")
print(f"  平均每次 Token: {total_tokens / len(runs) if runs else 0:.0f}")
print(f"  平均延遲: {total_latency / len(runs) if runs else 0:.2f}s")
