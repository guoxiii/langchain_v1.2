# tool_guardrails.py

"""
Tool Execution 控制：使用 wrap_tool_call 限制危險操作
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

# === 定義工具 ===
@tool
def read_file(path: str) -> str:
    """讀取檔案內容。"""
    # 模擬檔案讀取
    return f"檔案 {path} 的內容：Hello World!"

@tool
def delete_file(path: str) -> str:
    """刪除檔案。"""
    # 模擬檔案刪除
    return f"已刪除檔案：{path}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """發送電子郵件。"""
    # 模擬發送郵件
    return f"已發送郵件至 {to}，主題：{subject}"

@tool
def query_database(sql: str) -> str:
    """執行資料庫查詢。"""
    # 模擬資料庫查詢
    return f"查詢結果：共 42 筆資料"

# === 工具白名單與權限控制 Middleware ===
# 定義工具的風險等級
TOOL_RISK_LEVELS = {
    "read_file": "low",
    "query_database": "medium",
    "send_email": "high",
    "delete_file": "critical",
}

# 定義每個風險等級的處理方式
RISK_POLICIES = {
    "low": {"action": "allow"},
    "medium": {"action": "log"},
    "high": {"action": "confirm"},
    "critical": {"action": "block"},
}

@wrap_tool_call
async def tool_security_guard(request, handler):
    """
    工具安全守衛：根據風險等級控制工具執行。

    wrap_tool_call 的簽名：
    - request: ToolCallRequest 物件
      - request.tool_call["name"]  → 工具名稱
      - request.tool_call["args"]  → 工具輸入參數（dict）
      - request.tool_call["id"]    → 工具呼叫 ID
    - handler: callable，呼叫 await handler(request) 會真正執行工具

    你可以選擇：
    1. 直接呼叫 handler(request) 放行
    2. 用 request.override() 修改後再呼叫 handler()
    3. 不呼叫 handler()，返回 ToolMessage（攔截）
    """

    tool_name = request.tool_call["name"]
    tool_input = request.tool_call["args"]
    tool_call_id = request.tool_call["id"]

    risk_level = TOOL_RISK_LEVELS.get(tool_name, "high")
    policy = RISK_POLICIES.get(risk_level, {"action": "block"})

    print(f"🔧 工具呼叫：{tool_name}（風險等級：{risk_level}）")
    print(f"   參數：{tool_input}")

    if policy["action"] == "allow":
        # 低風險：直接放行
        return await handler(request)
    elif policy["action"] == "log":
        # 中風險：記錄後放行
        print(f"   📝 [LOG] 中風險操作已記錄")
        result = await handler(request)
        print(f"   📝 [LOG] 執行結果：{result}")
        return result
    elif policy["action"] == "confirm":
        # 高風險：需要確認（這裡模擬自動確認，實際應該用 HITL）
        print(f"   ⚠️ [CONFIRM] 高風險操作需要確認")
        # 在實際應用中，這裡會觸發 Human-in-the-Loop
        return await handler(request)
    elif policy["action"] == "block":
        # 極高風險：直接攔截，返回 ToolMessage 而非呼叫 handler
        print(f"   🚫 [BLOCK] 危險操作已被攔截")
        return ToolMessage(
            content=f"安全策略已阻止執行 {tool_name}。此操作需要管理員權限。",
            tool_call_id=tool_call_id,
        )

    # 未知風險等級，預設攔截
    return ToolMessage(
        content="未知的工具風險等級，操作已被攔截。",
        tool_call_id=tool_call_id,
    )


# === SQL Injection 防護 Middleware ===
@wrap_tool_call
async def sql_injection_guard(request, handler):
    """
    專門針對資料庫工具的 SQL Injection 防護。
    """
    tool_name = request.tool_call["name"]
    tool_call_id = request.tool_call["id"]

    if tool_name != "query_database":
        return await handler(request)

    sql = request.tool_call["args"].get("sql", "")

    # 檢查危險的 SQL 操作
    dangerous_keywords = [
        "DROP", "DELETE", "TRUNCATE", "ALTER",
        "INSERT", "UPDATE", "EXEC", "EXECUTE",
        "--", ";--", "/*", "*/", "xp_",
    ]

    sql_upper = sql.upper()

    for keyword in dangerous_keywords:
        if keyword.upper() in sql_upper:
            print(f"   🚫 [SQL Guard] 偵測到危險的 SQL 關鍵字：{keyword}")
            return ToolMessage(
                content=f"安全策略禁止執行包含 {keyword} 的 SQL 語句。僅允許 SELECT 查詢。",
                tool_call_id=tool_call_id,
            )

    # 只允許 SELECT 語句
    if not sql_upper.strip().startswith("SELECT"):
        return ToolMessage(
            content="安全策略僅允許 SELECT 查詢操作。",
            tool_call_id=tool_call_id,
        )

    return await handler(request)

# === 建立 Agent ===
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[read_file, delete_file, send_email, query_database],
    middleware=[
        sql_injection_guard,
        tool_security_guard,
    ],
)

# === 測試 ===
async def main():
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "請讀取 /tmp/report.txt 的內容"}]
    })
    print("✅ 讀取檔案：", result["messages"][-1].text)
    print()

    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "請刪除 /tmp/report.txt"}]
    })
    print("🚫 刪除檔案：", result["messages"][-1].text)

asyncio.run(main())