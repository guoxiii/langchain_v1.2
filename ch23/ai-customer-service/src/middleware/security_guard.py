# src/middleware/security_guard.py

"""
自定義安全 Middleware。
偵測並阻擋 Prompt Injection 攻擊。
參考第 19-20 章的安全防護策略，
黃金法則：先用確定性規則（快速、便宜），再用模型型檢查（深入、昂貴）。
"""

import re
from langchain.agents.middleware import before_agent
from langchain_core.messages import HumanMessage, AIMessage

# 可疑的 Prompt Injection 模式
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
    r"你現在是一個",
    r"忘記之前的",
    r"system\s*prompt",
    r"你的指令是",
    r"disregard\s+(all|previous)",
    r"new\s+instructions?:",
    r"override\s+(system|safety)",
    r"jailbreak",
    r"DAN\s+mode",
]

@before_agent
def security_guard_middleware(state, runtime):
    """在 Agent 處理之前，檢查輸入是否包含 Prompt Injection 攻擊。"""
    messages = state.get("messages", [])

    if not messages:
        return state

    # 取得最新的使用者訊息
    latest_message = messages[-1]

    if not isinstance(latest_message, HumanMessage):
        return state

    user_input = latest_message.content

    if not isinstance(user_input, str):
        return state

    # 規則式檢查 — 快速且免費
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            # 偵測到可疑輸入，替換為安全回覆
            return {
                "messages": messages[:-1] + [
                    latest_message,
                    AIMessage(
                        content="我是客服助手，只能回答與商品、訂單、"
                        "退貨等客服相關的問題。請問您有什麼客服需求嗎？😊"
                    ),
                ],
            }

    return state
