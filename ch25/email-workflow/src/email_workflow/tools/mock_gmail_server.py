# src/email_workflow/tools/mock_gmail_server.py

"""
模擬 Gmail MCP Server — 用 FastMCP 建構

這個 Server 模擬真實 Gmail MCP 的兩個核心工具：
- gmail_search：搜尋郵件（回傳郵件 ID 清單）
- gmail_read：讀取單封郵件內容

用途：在沒有真實 Gmail 連線的情況下，
讓整個郵件處理工作流能完整跑通。
等之後要接真的 Gmail，只要把 MCP 連線設定換掉就好，
工作流的其他程式碼完全不用改。
"""

from datetime import datetime, timedelta
from fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP(
    name="mock-gmail",
    instructions="模擬 Gmail MCP Server，提供郵件搜尋與讀取功能。",
)

# === 模擬郵件資料庫 ===
# 三封郵件分別對應工作流的三條處理路線：客訴、報價、一般郵件
NOW = datetime.now()

MOCK_EMAILS = {
    "msg-001": {
        "id": "msg-001",
        "sender": "angry_customer@example.com",
        "subject": "你們的產品有嚴重問題！",
        "body": (
            "我上週買的 PURIFY 止汗噴霧，用了之後皮膚起紅疹，"
            "非常不滿意！我要求全額退款，否則我會在社群媒體上公開投訴。"
            "請盡快處理，我已經等了三天都沒人回覆！"
        ),
        "date": (NOW - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "labels": ["INBOX", "UNREAD"],
    },
    "msg-002": {
        "id": "msg-002",
        "sender": "buyer@bigretail.com",
        "subject": "Re: PURIFY 體香膏批發報價詢問",
        "body": (
            "您好，我是大潤發的採購經理。"
            "我們對 PURIFY 體香膏系列很有興趣，"
            "想詢問 1000 組以上的批發價格，"
            "以及是否能提供客製化包裝。"
            "請提供正式報價單，謝謝。"
        ),
        "date": (NOW - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "labels": ["INBOX", "UNREAD"],
    },
    "msg-003": {
        "id": "msg-003",
        "sender": "newsletter@medium.com",
        "subject": "本週精選：AI Agent 開發趨勢",
        "body": (
            "本週精選文章：如何用 LangGraph 建構企業級 AI Agent、"
            "MCP 協定的最新發展、以及 RAG 系統的效能優化技巧。"
            "點擊閱讀更多..."
        ),
        "date": (NOW - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
        "labels": ["INBOX", "UNREAD"],
    },
}

@mcp.tool()
def gmail_search(query: str, max_results: int = 10) -> list[dict]:
    """
    搜尋 Gmail 郵件。

    Args:
        query: Gmail 搜尋語法，例如 'is:unread newer_than:1d'
        max_results: 最多回傳幾封，預設 10

    Returns:
        符合條件的郵件摘要清單（id, sender, subject, date）
    """
    # 模擬搜尋邏輯：只要 query 包含 "unread" 就回傳所有未讀郵件
    results = []
    for email in MOCK_EMAILS.values():
        if "unread" in query.lower() and "UNREAD" in email["labels"]:
            results.append({
                "id": email["id"],
                "sender": email["sender"],
                "subject": email["subject"],
                "date": email["date"],
            })
        elif not query:  # 空查詢回傳全部
            results.append({
                "id": email["id"],
                "sender": email["sender"],
                "subject": email["subject"],
                "date": email["date"],
            })

    return results[:max_results]

@mcp.tool()
def gmail_read(message_id: str) -> dict:
    """
    讀取單封 Gmail 郵件的完整內容。

    Args:
        message_id: 郵件 ID

    Returns:
        郵件完整資訊（id, sender, subject, body, date, labels）
    """
    if message_id in MOCK_EMAILS:
        return MOCK_EMAILS[message_id]
    else:
        return {"error": f"找不到郵件 ID: {message_id}"}

if __name__ == "__main__":
    # 以 stdio 模式啟動，供 langchain-mcp-adapters 連接
    mcp.run(transport="stdio")