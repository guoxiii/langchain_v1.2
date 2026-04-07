# src/email_workflow/tools/gmail_mcp.py

"""Gmail MCP 連線設定 — 讓 Agent 能讀取 Gmail 信箱"""

import sys
from pathlib import Path

def get_mcp_client_config() -> dict:
    """
    取得 MCP Client 配置

    目前使用 stdio 傳輸方式連接模擬 Gmail MCP Server。
    等之後要接真的 Gmail，只要把這裡的設定換成真實 Server 就好：

    真實 Gmail MCP 範例（使用 @gongrzhe/server-gmail-autoauth-mcp）：
        return {
            "gmail": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
            }
        }
    """

    # 找到 mock server 的路徑（相對於本檔案）
    mock_server_path = str(
        Path(__file__).parent / "mock_gmail_server.py"
    )

    return {
        "gmail": {
            "transport": "stdio",
            "command": sys.executable,  # 使用當前 Python 直譯器
            "args": [mock_server_path],
        },
    }