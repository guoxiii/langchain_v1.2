# ch16/filesystem_agent.py
from dotenv import load_dotenv
from deepagents import create_deep_agent

load_dotenv()

# 若要真的做「研究」,這裡該注入搜尋工具(例如 Tavily)
# 若純粹示範 filesystem + todos,就把 prompt 改成「根據你已知的知識整理」
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="""你是一位技術研究員。請依照以下流程完成任務:
1. 先用 write_todos 建立研究計畫
2. 根據你已知的知識,將各工具的特性分別用 write_file 存到 /research/ 目錄下(例如 /research/uv.md、/research/pip.md、/research/poetry.md)
3. 綜合上述筆記,將最終比較報告寫到 /output/report.md
4. 報告使用繁體中文,結構需包含:簡介、各工具特色、優缺點比較表、結論
""",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "請研究 uv 套件管理器的優缺點,並與 pip 和 poetry 比較"}]
})

# --- 驗證 agent 是否真的照 prompt 執行 ---
print("=" * 60)
print("📋 Todos")
print("=" * 60)

for todo in result.get("todos", []):
    print(f"  [{todo.get('status', '?')}] {todo.get('content', todo)}")

print("\n" + "=" * 60)
print("📁 虛擬檔案系統")
print("=" * 60)

for path in sorted(result.get("files", {}).keys()):
    size = len(result["files"][path])
    print(f"  {path}  ({size} chars)")

print("\n" + "=" * 60)
print("📄 /output/report.md 內容")
print("=" * 60)
print(result.get("files", {}).get("/output/report.md", "(未生成)"))

print("\n" + "=" * 60)
print("💬 Agent 最終回覆")
print("=" * 60)
print(result["messages"][-1].text)