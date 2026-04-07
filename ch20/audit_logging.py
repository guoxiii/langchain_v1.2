# audit_logging.py

"""
安全審計日誌：記錄所有 Agent 的關鍵操作
"""

from dotenv import load_dotenv
load_dotenv()

import json
import logging
from datetime import datetime, timezone
from langchain.agents import create_agent
from langchain.agents.middleware import before_agent, after_model, wrap_tool_call
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# 設定審計日誌
audit_logger = logging.getLogger("agent.audit")
audit_logger.setLevel(logging.INFO)

# 輸出到檔案
file_handler = logging.FileHandler("agent_audit.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
))
audit_logger.addHandler(file_handler)


def log_audit_event(event_type: str, details: dict):
    """記錄審計事件"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **details,
    }
    audit_logger.info(json.dumps(event, ensure_ascii=False))


@tool
def search_records(query: str) -> str:
    """搜尋銷售記錄,回傳結構化的訂單資訊。"""
    # 模擬回傳具體資料,讓 Gemini 比較難偷懶跳過
    return (
        f"查詢條件:{query}\n"
        f"找到 3 筆記錄:\n"
        f"- 訂單 #A1024 | 客戶:王小明 | 金額:NT$2,500 | 日期:2026-04-05\n"
        f"- 訂單 #A1025 | 客戶:李美華 | 金額:NT$4,800 | 日期:2026-04-05\n"
        f"- 訂單 #A1026 | 客戶:陳大衛 | 金額:NT$1,200 | 日期:2026-04-06"
    )


# === 審計 Middleware ===
@before_agent
def audit_input(state, runtime):
    """記錄所有使用者輸入"""
    messages = state["messages"]

    if messages and isinstance(messages[-1], HumanMessage):
        log_audit_event("USER_INPUT", {
            "content_length": len(messages[-1].text),
            "content_preview": messages[-1].text[:100],
        })

    return None


@after_model
def audit_output(state, runtime):
    """記錄模型每一次輸出,並區分『工具決策』與『最終答覆』"""
    messages = state["messages"]
    if not messages:
        return None

    last = messages[-1]
    if not isinstance(last, AIMessage):
        return None

    # 有 tool_calls 表示這是中間決策,沒有則是最終答覆
    if last.tool_calls:
        log_audit_event("AGENT_TOOL_DECISION", {
            "content_length": len(last.text),
            "content_preview": last.text[:100],
            "tool_calls": [tc["name"] for tc in last.tool_calls],
        })
    else:
        log_audit_event("AGENT_FINAL_OUTPUT", {
            "content_length": len(last.text),
            "content_preview": last.text[:100],
        })

    return None


@wrap_tool_call
def audit_tool_call(request, handler):
    """記錄所有工具呼叫(前後)"""
    tool_call = request.tool_call

    log_audit_event("TOOL_CALL_START", {
        "tool": tool_call["name"],
        "input": str(tool_call["args"])[:200],
    })

    result = handler(request)

    # 穩健取出工具回傳內容,避免未來 artifact / 多 block 情境出錯
    result_content = result.content if hasattr(result, "content") else str(result)

    log_audit_event("TOOL_CALL_END", {
        "tool": tool_call["name"],
        "result_preview": str(result_content)[:200],
    })

    return result


# === 建立 Agent ===
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[search_records],
    system_prompt=(
        "你是一位專業的銷售分析助理。"
        "當使用者詢問銷售資料時,務必呼叫 search_records 工具取得資料,"
        "並將工具回傳的訂單明細『完整、清楚地』呈現給使用者,不要只說『我已查詢完畢』。"
    ),
    middleware=[
        audit_input,
        audit_output,
        audit_tool_call,
    ],
)

# === 測試 ===
result = agent.invoke({
    "messages": [{"role": "user", "content": "請搜尋最近的銷售記錄"}]
})

print("✅ 結果:", result["messages"][-1].text)
print("\n📋 審計日誌已寫入 agent_audit.log")

# === 把本次執行的審計軌跡印出來,讓讀者直接感受「審計」發生了什麼 ===
print("\n" + "=" * 60)
print("📜 本次執行的審計軌跡:")
print("=" * 60)

with open("agent_audit.log", "r", encoding="utf-8") as f:
    lines = f.readlines()
    # 顯示最後幾筆:USER_INPUT + TOOL_DECISION + TOOL_START + TOOL_END + FINAL_OUTPUT
    for line in lines[-5:]:
        # 嘗試美化 JSON 輸出
        try:
            # 格式:時間 | 等級 | JSON
            prefix, json_str = line.rstrip().split(" | INFO | ", 1)
            event = json.loads(json_str)
            print(f"\n[{event['event_type']}]")
            for k, v in event.items():
                if k in ("timestamp", "event_type"):
                    continue
                print(f"  {k}: {v}")
        except Exception:
            print(line.rstrip())