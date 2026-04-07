# src/tools/mcp_tools.py

"""
載入 MCP Server 工具，轉換為 LangChain 工具格式。
"""

from langchain_mcp_adapters.client import MultiServerMCPClient

def get_mcp_client_config():
    """取得 MCP Client 設定。"""
    return {
        "ticket-system": {
            "command": "uv",
            "args": [
                "run",
                "python",
                "-m",
                "src.mcp_servers.ticket_server",
            ],
            "transport": "stdio",
        }
    }

async def load_mcp_tools():
    """載入所有 MCP Server 的工具。"""
    client = MultiServerMCPClient(get_mcp_client_config())
    tools = await client.get_tools()
    return tools, client
