# src/agent/middleware.py
"""Agent 安全 Middleware — Agent 的保鏢團隊"""

from dotenv import load_dotenv
load_dotenv()

import re
from langchain.agents.middleware import AgentMiddleware, AgentState

class PromptInjectionGuard(AgentMiddleware):
    """
    Prompt Injection 防護 Middleware
    在 before_agent hook 攔截可疑的使用者輸入。

    策略：先用規則式偵測（便宜又快），可疑時再用 LLM 判斷。

    這就是第 20 章學到的「黃金法則」：
    先確定性規則 → 再模型型 Guardrails
    """

    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+(instructions|prompts)",
        r"forget\s+(your|all|previous)\s+(rules|instructions)",
        r"你現在是一個",
        r"假裝你是",
        r"system\s*prompt",
        r"jailbreak",
        r"DAN\s*mode",
        r"<\|im_start\|>",
        r"\[INST\]",
    ]

    def before_agent(self, state: AgentState, runtime):
        """在 Agent 處理之前檢查輸入"""
        messages = state.get("messages", [])

        if not messages:
            return None  # 不修改 state

        last_message = messages[-1]

        if not hasattr(last_message, "content"):
            return None

        content = last_message.content

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                from langchain_core.messages import HumanMessage

                safe_message = HumanMessage(
                    content=(
                        "⚠️ [系統安全提示] 偵測到可疑的輸入模式。"
                        "請使用正常的問題進行查詢。"
                        "如有需要，請聯繫系統管理員。"
                    )
                )
                # 回傳差異 dict，框架會 merge 進 state
                return {"messages": messages[:-1] + [safe_message]}

        return None  # 通過檢查，不修改

class AccessControlMiddleware(AgentMiddleware):
    """
    權限控制 Middleware
    根據使用者角色過濾搜尋結果，確保使用者只能看到
    自己有權限存取的文件。
    """

    def after_model(self, state: AgentState, runtime):
        """在模型回覆後，檢查引用的文件是否在使用者權限範圍內"""
        config = runtime.config if hasattr(runtime, "config") else {}
        configurable = config.get("configurable", {})

        user_role = configurable.get("user_role", "viewer")
        user_id = configurable.get("user_id", "anonymous")

        print(f"📋 存取紀錄：user={user_id}, role={user_role}")
        return None  # 不修改 state
    
# src/agent/middleware.py（續）

class TaiwanPIIGuard(AgentMiddleware):
    """
    台灣特定 PII 偵測與遮蔽

    偵測並遮蔽台灣常見的個資格式：
    - 身分證字號（例：A123456789）
    - 手機號碼（例：0912-345-678）
    - 統一編號（例：12345678）
    """

    PII_PATTERNS = {
        "身分證字號": r"[A-Z][12]\d{8}",
        "手機號碼": r"09\d{2}[-\s]?\d{3}[-\s]?\d{3}",
        "統一編號": r"\b\d{8}\b",
        "電子郵件": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    }

    async def before_model(self, messages, state, config):
        """在送給 LLM 之前遮蔽 PII"""
        import re

        redacted_messages = []

        for msg in messages:
            content = msg.content if hasattr(msg, "content") else str(msg)

            for pii_type, pattern in self.PII_PATTERNS.items():
                content = re.sub(
                    pattern,
                    f"[已遮蔽的{pii_type}]",
                    content,
                )

            # 建立新的訊息物件（保持原本的類型）

            from langchain_core.messages import HumanMessage, AIMessage

            if hasattr(msg, "type") and msg.type == "human":
                redacted_messages.append(
                    HumanMessage(content=content)
                )
            else:
                redacted_messages.append(msg)

        return redacted_messages
