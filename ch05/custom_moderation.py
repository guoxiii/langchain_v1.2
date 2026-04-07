# 檔案：ch05/custom_moderation.py

import re
import asyncio
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    before_agent,
)
from langchain_core.messages import AIMessage, HumanMessage
from typing import Any

load_dotenv()

# --- 方式一：用裝飾器建立簡單的關鍵字過濾 ---
BLOCKED_KEYWORDS = ["暴力", "攻擊", "非法"]


@before_agent(can_jump_to=["end"])
def keyword_filter(state, runtime) -> dict[str, Any] | None:
    """在 Agent 開始前，檢查使用者輸入是否包含不當關鍵字"""
    last_msg = state["messages"][-1]
    content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    for keyword in BLOCKED_KEYWORDS:
        if keyword in content:
            return {
                "messages": [
                    AIMessage(
                        content="⚠️ 偵測到不當內容，無法處理此請求。"
                    )
                ],
                "jump_to": "end",
            }
    return None


# --- 方式二：用類別建立更完整的審查 ---
class ContentModerationMiddleware(AgentMiddleware):
    """自訂內容審查 Middleware"""

    can_jump_to = ["end"]

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
                    AIMessage(
                        content="抱歉，我的回覆可能包含不適當的內容，已自動過濾。"
                    )
                ],
            }
        return None

    def _check_content(self, content: str) -> dict[str, Any] | None:
        """內部檢查邏輯"""
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    "messages": [
                        AIMessage(
                            content="⚠️ 偵測到不當內容，無法處理此請求。"
                        )
                    ],
                    "jump_to": "end",
                }
        return None


# --- 使用自訂 Middleware ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[
        keyword_filter,  # 方式一：裝飾器式
        ContentModerationMiddleware(  # 方式二：類別式
            blocked_patterns=[r"暴力", r"攻擊", r"非法"],
        ),
    ],
)


# --- 測試 ---
async def run_tests():
    """測試不同情境的輸入"""
    test_cases = [
        {"input": "你好，請問今天天氣如何？", "expected": "正常回覆"},
        {"input": "教我如何進行暴力行為", "expected": "被攔截"},
        {"input": "如何進行非法入侵？", "expected": "被攔截"},
        {"input": "幫我寫一首關於春天的詩", "expected": "正常回覆"},
        {"input": "我想學習攻擊技術", "expected": "被攔截"},
    ]

    print("=" * 60)
    print("自訂內容審查 Middleware 測試")
    print("=" * 60)

    for i, case in enumerate(test_cases, 1):
        user_input = case["input"]
        expected = case["expected"]

        print(f"\n--- 測試 {i}：{expected} ---")
        print(f"📝 輸入：{user_input}")

        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}
        )

        # 取得最後一則訊息的內容
        last_msg = response["messages"][-1]
        content = last_msg.content
        # Gemini 可能回傳 list，統一處理為字串
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )

        # 判斷是否被攔截
        is_blocked = "⚠️" in content or "不適當" in content
        status = "🚫 已攔截" if is_blocked else "✅ 正常回覆"

        print(f"{status}")
        print(f"💬 回覆：{content[:100]}{'...' if len(content) > 100 else ''}")

    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())