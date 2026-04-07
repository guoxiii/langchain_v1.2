"""
檔案:circuit_breaker_demo.py
自訂 Circuit Breaker Middleware（斷路器）

想像你家的配電箱：電流超載時,斷路器會自動跳脫,
保護家裡的電器不被燒壞，等你排除問題後,再手動合上開關。
這個 Middleware 對 LLM 做的事情完全一樣，
連續失敗太多次,就先「斷電」,直接回傳降級回應,
等冷卻時間過了再嘗試恢復。
"""

import time
from typing import Callable
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)
from langchain.messages import AIMessage, HumanMessage

# ============================================================
# 方法一：Class-based Middleware（適合需要多個 hook 或複雜設定）
# ============================================================

class CircuitBreakerMiddleware(AgentMiddleware):
    """
    斷路器 Middleware：三種狀態輪轉

    CLOSED（正常通電）→ 失敗累積到門檻 → OPEN（斷電）
    OPEN（斷電）→ 冷卻時間到 → HALF_OPEN（試探）
    HALF_OPEN（試探）→ 成功 → CLOSED ／ 失敗 → OPEN
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 30,
        fallback_message: str = "⚡ 服務暫時忙碌，請稍後再試。",
    ):
        super().__init__()
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback_message = fallback_message

        # 內部狀態
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._state = "CLOSED"  # CLOSED | OPEN | HALF_OPEN

    def _make_fallback_response(self) -> ModelResponse:
        """建立降級回應的 ModelResponse"""
        return ModelResponse(
            result=[AIMessage(content=self.fallback_message)]
        )

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """攔截模型呼叫，依據斷路器狀態決定行為"""

        # ── OPEN 狀態：檢查是否該進入 HALF_OPEN ──
        if self._state == "OPEN":
            elapsed = time.time() - self._last_failure_time
            if elapsed > self.recovery_timeout:
                self._state = "HALF_OPEN"
                print(f"  🔄 斷路器半開：冷卻 {elapsed:.0f}s 已過，嘗試恢復...")
            else:
                remaining = self.recovery_timeout - elapsed
                print(f"  🔴 斷路器開啟：跳過模型呼叫，剩餘冷卻 {remaining:.0f}s")
                return self._make_fallback_response()

        # ── CLOSED 或 HALF_OPEN：嘗試正常呼叫 ──
        try:
            response = handler(request)

            # 成功！重置斷路器
            if self._state == "HALF_OPEN":
                print("  🟢 斷路器恢復正常（HALF_OPEN → CLOSED）")
            self._failure_count = 0
            self._state = "CLOSED"
            return response

        except Exception as e:
            # 失敗！累積計數
            self._failure_count += 1
            self._last_failure_time = time.time()
            print(
                f"  ⚠️  模型呼叫失敗（{self._failure_count}/{self.failure_threshold}）："
                f" {type(e).__name__}: {e}"
            )

            if self._failure_count >= self.failure_threshold:
                self._state = "OPEN"
                print(
                    f"  🔴 斷路器跳脫！連續失敗 {self._failure_count} 次，"
                    f"進入 OPEN 狀態（冷卻 {self.recovery_timeout}s）"
                )

            # 重新拋出，讓外層的 ModelFallbackMiddleware 等有機會處理
            raise

# ============================================================
# 示範執行
# ============================================================

def main():
    """示範 CircuitBreakerMiddleware 的基本用法"""

    print("=" * 60)
    print("🔌 Circuit Breaker Middleware 示範")
    print("=" * 60)

    # 建立帶有斷路器的 Agent
    agent = create_agent(
        model="google_genai:gemini-2.5-flash",
        tools=[],
        middleware=[
            CircuitBreakerMiddleware(
                failure_threshold=3,    # 連續失敗 3 次就跳脫
                recovery_timeout=10,    # 冷卻 10 秒後嘗試恢復
            ),
        ],
        system_prompt="你是一個友善的助手，請用繁體中文回答。",
    )

    # 正常呼叫
    print("\n📨 發送正常請求...")
    result = agent.invoke(
        {"messages": [HumanMessage(content="用一句話解釋什麼是斷路器模式？")]}
    )
    # 取得最後一則 AI 回覆
    last_msg = result["messages"][-1]
    print(f"✅ 回覆：{last_msg.content[:100]}...")

    print("\n" + "=" * 60)
    print("💡 斷路器目前狀態：正常運作（CLOSED）")
    print("   如果模型連續失敗 3 次，就會自動跳脫保護！")
    print("=" * 60)

if __name__ == "__main__":
    main()