# structured_content_server.py

"""示範回傳結構化內容的 MCP Server"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DataService")

@mcp.tool()
def get_report_summary(report_id: str) -> dict:
    """取得報表摘要。回傳結構化的報表資料。

    Args:
        report_id: 報表 ID
    Returns:
        包含標題、摘要、數據的報表資料
    """

    return {
        "report_id": report_id,
        "title": "2024 Q4 銷售報表",
        "summary": "第四季度銷售額較上季成長 15%",
        "metrics": {
            "total_revenue": 1500000,
            "growth_rate": 0.15,
            "top_product": "智能手錶 Pro",
        },
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
