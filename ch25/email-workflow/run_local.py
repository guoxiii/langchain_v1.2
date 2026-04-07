# run_local.py

"""本地執行工作流 — 測試用"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.email_workflow.graph import compile_workflow

async def main():
    graph = compile_workflow()

    # 啟動工作流
    config = {"configurable": {"thread_id": "daily-run-20260312"}}
    print("🚀 啟動郵件處理工作流...")
    print("=" * 50)

    async for event in graph.astream(
        {"messages": []},
        config=config,
        stream_mode="updates",
    ):
        # 印出每個節點的執行狀態
        for node_name, node_output in event.items():
            status = node_output.get("workflow_status", "processing")
            print(f"📍 節點 [{node_name}] 完成 | 狀態: {status}")

    print("=" * 50)
    print("✅ 工作流執行完成！")

if __name__ == "__main__":
    asyncio.run(main())
