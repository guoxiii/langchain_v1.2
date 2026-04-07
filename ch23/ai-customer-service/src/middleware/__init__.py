# src/middleware/__init__.py

"""
Middleware 統一管理模組。
組合所有 Middleware 並管理執行順序。
"""

from src.middleware.pii_config import create_pii_middlewares
from src.middleware.summarization_config import create_summarization_middleware
from src.middleware.hitl_config import create_hitl_middleware
from src.middleware.security_guard import security_guard_middleware

def build_middleware_stack():
    """建構完整的 Middleware Stack。
    執行順序很重要！
    1. 安全檢查（最先執行，阻擋惡意輸入）
    2. PII 遮蔽（在 LLM 看到訊息之前處理敏感資訊）
    3. 對話摘要（管理 Context Window）
    4. HITL（在工具執行前進行人工審核）
    """

    middleware = []

    # 1. 安全檢查 — 第一道防線
    middleware.append(security_guard_middleware)

    # 2. PII 遮蔽 — 保護客戶資料
    middleware.extend(create_pii_middlewares())

    # 3. 對話摘要 — 管理 Context Window
    middleware.append(create_summarization_middleware())

    # 4. HITL — 人工審核閘門
    middleware.append(create_hitl_middleware())

    return middleware
