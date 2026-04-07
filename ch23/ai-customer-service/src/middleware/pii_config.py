# src/middleware/pii_config.py

"""
PII（個人識別資訊）遮蔽 Middleware 設定。
保護客戶的敏感資料不被 LLM 處理或記錄。
"""

from langchain.agents.middleware import PIIMiddleware

def create_pii_middlewares():
    """建立 PII 遮蔽 Middleware 列表。"""
    return [
        # 遮蔽電子郵件地址
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        # 遮蔽信用卡號碼（只顯示最後 4 碼）
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        # 自定義：遮蔽台灣身分證字號
        PIIMiddleware(
            "tw_national_id",
            detector=r"[A-Z][12]\d{8}",
            strategy="redact",
            apply_to_input=True,
        ),
        # 自定義：遮蔽台灣手機號碼
        PIIMiddleware(
            "tw_phone",
            detector=r"09\d{2}-?\d{3}-?\d{3}",
            strategy="mask",
            apply_to_input=True,
        ),
    ]
