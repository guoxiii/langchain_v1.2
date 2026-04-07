# src/agent/tracking.py

"""
LangSmith 追蹤設定。
為每次對話附加自定義 metadata，方便後續分析。
"""

def create_tracking_config(
    thread_id: str,
    customer_id: str | None = None,
    channel: str = "web",
) -> dict:
    """建立包含追蹤資訊的 config。

    Args:
        thread_id: 對話 Thread ID
        customer_id: 客戶 ID（選填）
        channel: 對話來源（web / app / line）

    Returns:
        傳給 agent.invoke() 的 config dict
    """

    return {
        "configurable": {
            "thread_id": thread_id,
        },
        "metadata": {
            "customer_id": customer_id or "anonymous",
            "channel": channel,
            "service": "customer-support",
            "version": "1.0.0",
        },
        "tags": ["customer-service", channel],
    }
