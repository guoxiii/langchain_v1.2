# 檔案：ch05/09_custom_moderation.py

import os
import re
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    before_agent,
    after_agent,
)
from langchain_core.messages import AIMessage
from typing import Any

load_dotenv()

# --- 方式一：用裝飾器建立簡單的關鍵字過濾 ---
# 定義不允許的關鍵字清單
BLOCKED_KEYWORDS = ["暴力", "攻擊", "非法"]

@before_agent
def keyword_filter(state, runtime) -> dict[str, Any] | None:
    """在 Agent 開始前，檢查使用者輸入是否包含不當關鍵字"""
    last_msg = state["messages"][-1]
    content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    for keyword in BLOCKED_KEYWORDS:
        if keyword in content:
            return {
                "messages": [
                    AIMessage(
                        content=f"⚠️ 偵測到不當內容，無法處理此請求。"
                    )
                ],
                "jump_to": "end",
            }
    return None
# --- 方式二：用類別建立更完整的審查 ---
class ContentModerationMiddleware(AgentMiddleware):
    """自訂內容審查 Middleware"""
    def __init__(self, blocked_patterns: list[str] | None = None):
        super().__init__()
        self.blocked_patterns = blocked_patterns or []

    def before_agent(self, state, runtime) -> dict[str, Any] | None:
        """檢查使用者輸入"""
        last_msg = state["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        return self._check_content(content)

    def after_agent(self, state, runtime) -> dict[str, Any] | None:
        """檢查 Agent 輸出"""
        last_msg = state["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        violation = self._check_content(content)

        if violation:
            return {
                "messages": [
                    AIMessage(content="抱歉，我的回覆可能包含不適當的內容，已自動過濾。")
                ],
            }

        return None

    def _check_content(self, content: str) -> dict[str, Any] | None:
        """內部檢查邏輯"""
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    "messages": [
                        AIMessage(content="⚠️ 偵測到不當內容，無法處理此請求。")
                    ],
                    "jump_to": "end",
                }

        return None

# --- 使用自訂 Middleware ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],

    middleware=[
        ContentModerationMiddleware(
            blocked_patterns=[r"暴力", r"攻擊", r"非法"]
        ),
    ],
)
