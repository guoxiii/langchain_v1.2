# tool_call_limit.py
"""
ToolCallLimitMiddleware:限制 Agent 單次運行的工具呼叫次數

當 LLM 陷入「工具呼叫迴圈」(例如一直重複搜尋卻永遠不滿足),
ToolCallLimitMiddleware 就像斷路器,能保護你的 API 額度不被燒光。
"""
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool


# === 設計一個「會誘導 LLM 反覆呼叫」的工具 ===
# 故意回傳不完整的結果,並在描述裡鼓勵 LLM「再搜一次」,
# 這樣就能穩定複現工具呼叫迴圈,讓讀者看到 middleware 的攔截效果。
search_count = 0


@tool
def web_search(query: str) -> str:
    """搜尋網路資訊。若搜尋結果標示為「不完整」,請換更精確的關鍵字再搜尋一次,直到取得完整資訊為止。"""
    global search_count
    search_count += 1
    return (
        f"[第 {search_count} 次搜尋結果] 找到部分關於 '{query}' 的片段資訊,"
        f"但這份資料【不完整】,建議換更精確的關鍵字再搜尋一次以取得完整內容。"
    )


# === 建立 Agent,加上工具呼叫次數限制 ===
# run_limit=3 代表:單次 agent.invoke() 執行中,
# 累計工具呼叫次數達到 3 次就會被攔截,Agent 直接結束不再呼叫 LLM。
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[web_search],
    system_prompt=(
        "你是一位嚴謹的研究助理。面對使用者的問題,"
        "你必須透過 web_search 工具查證;如果搜尋結果標示為『不完整』,"
        "就必須換不同關鍵字繼續搜尋,直到取得完整資訊才能回答。"
    ),
    middleware=[
        ToolCallLimitMiddleware(run_limit=3),
    ],
)

# === 測試:問一個會誘發多次搜尋的問題 ===
print("--- 測試:LLM 陷入重複搜尋迴圈,被 ToolCallLimitMiddleware 攔截 ---\n")
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "請幫我徹底調查『LangChain 1.2 的 middleware 機制』,要完整、詳細。"
    }]
})

# === 觀察結果 ===
print(f"📊 web_search 實際被呼叫次數:{search_count}(上限 3 次)\n")
print("--- 完整訊息鏈 ---")
for i, msg in enumerate(result["messages"]):
    msg_type = type(msg).__name__
    # 工具呼叫的 AIMessage 要特別顯示它呼叫了哪個工具
    if isinstance(msg, AIMessage) and msg.tool_calls:
        tool_names = ", ".join(tc["name"] for tc in msg.tool_calls)
        print(f"[{i}] {msg_type}(tool_calls): 呼叫 {tool_names}")
    elif isinstance(msg, ToolMessage):
        preview = str(msg.content)[:60].replace("\n", " ")
        print(f"[{i}] {msg_type}: {preview}...")
    else:
        preview = msg.text[:60].replace("\n", " ") if hasattr(msg, "text") else ""
        print(f"[{i}] {msg_type}: {preview}...")

print(f"\n--- Agent 最終回覆 ---")
print(result["messages"][-1].text)