# src/tools/escalation.py

"""
人工轉接工具。
當 AI 判斷無法處理時，使用此工具將對話轉接給真人客服。
"""

import json
from datetime import datetime
from langchain_core.tools import tool

@tool
def escalate_to_human(
    reason: str,
    customer_sentiment: str,
    conversation_summary: str,
) -> str:
    """將對話轉接給真人客服。
    當遇到以下情況時使用此工具：
    - 客戶明確要求與真人對話
    - 客戶情緒非常激動
    - 涉及退款金額爭議或法律問題
    - AI 無法回答的複雜問題

    Args:
        reason: 轉接原因（customer_request / emotional_escalation / refund_dispute / legal_issue / complex_issue）
        customer_sentiment: 客戶當前情緒（neutral / frustrated / angry / urgent）
        conversation_summary: 對話摘要，幫助真人客服快速了解狀況

    Returns:
        轉接結果資訊
    """

    # 在真實環境中，這裡會：
    # 1. 呼叫客服排隊系統 API
    # 2. 將對話記錄傳給真人客服的介面
    # 3. 通知真人客服有新的轉接

    escalation_id = f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return json.dumps(
        {
            "success": True,
            "escalation_id": escalation_id,
            "message": "已將您的對話轉接給真人客服，請稍候。",
            "estimated_wait_time": "約 3-5 分鐘",
            "queue_position": 2,
            "note_to_human_agent": {
                "reason": reason,
                "sentiment": customer_sentiment,
                "summary": conversation_summary,
            },
        },
        ensure_ascii=False,
    )
