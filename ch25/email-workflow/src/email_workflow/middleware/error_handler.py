# src/email_workflow/middleware/error_handler.py

"""錯誤處理 Middleware — 讓工作流更堅韌"""

from __future__ import annotations
from langchain.agents.middleware import (
    wrap_model_call,
    ModelRequest,
    ModelResponse,
)

import asyncio
import logging
logger = logging.getLogger(__name__)

@wrap_model_call
async def retry_on_error(
    request: ModelRequest, handler
) -> ModelResponse:
    """
    帶有指數退避的重試 Middleware
    當 LLM 呼叫失敗時（如 API rate limit），
    自動等待一段時間後重試。
    等待時間會隨著重試次數指數增長：

    第 1 次等 2 秒，第 2 次等 4 秒，第 3 次等 8 秒。

    就像是打電話佔線時，你不會一直瘋狂重撥，
    而是等一下再試，每次等久一點。
    """
    max_retries = 3
    base_delay = 2  # 基礎延遲秒數

    for attempt in range(max_retries + 1):
        try:
            return await handler(request)
        except Exception as e:
            if attempt == max_retries:
                logger.error(
                    f"❌ LLM 呼叫在 {max_retries} 次重試後仍然失敗：{e}"
                )
                raise

            delay = base_delay * (2 ** attempt)

            logger.warning(
                f"⚠️ LLM 呼叫失敗（第 {attempt + 1} 次），"
                f"{delay} 秒後重試... 錯誤：{e}"
            )

            await asyncio.sleep(delay)
