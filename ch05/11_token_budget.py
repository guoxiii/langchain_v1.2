# 檔案：ch05/11_token_budget.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage
from typing import Any

load_dotenv()

class TokenBudgetMiddleware(AgentMiddleware):
    """
    Token 預算控制器
    追蹤每次對話的 Token 使用量，超過預算時強制結束。
    """
    def __init__(self, max_tokens: int = 10000):
        super().__init__()
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def _estimate_tokens(self, text: str) -> int:
        """簡單的 Token 估算（英文約 4 字元/Token，中文約 2 字元/Token）"""
        # 這是粗略估算，生產環境建議使用 tiktoken
        return len(text) // 3

    @hook_config(can_jump_to=["end"])
    def before_model(self, state, runtime) -> dict[str, Any] | None:
        """在每次模型呼叫前，檢查 Token 預算"""
        # 估算目前所有訊息的 Token 數
        total_tokens = sum(
            self._estimate_tokens(
                msg.content if hasattr(msg, "content") and msg.content else ""
            )

            for msg in state["messages"]
        )

        self.used_tokens = total_tokens

        if total_tokens >= self.max_tokens:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            f"⚠️ Token 預算已用盡（{total_tokens}/{self.max_tokens}）。"
                            "對話即將結束。"
                        )
                    )
                ],
                "jump_to": "end",
            }

        remaining = self.max_tokens - total_tokens
        print(f"💰 Token 預算：已用 {total_tokens} / 上限 {self.max_tokens}，剩餘 {remaining}")

        return None

# --- 使用 ---
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[TokenBudgetMiddleware(max_tokens=5000)],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "請詳細解釋 Transformer 的自注意力機制"}]}
)

print(result["messages"][-1].content)
