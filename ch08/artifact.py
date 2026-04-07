# ch08/artifact.py

from dotenv import load_dotenv

load_dotenv()

from langchain.tools import tool

@tool(response_format="content_and_artifact")
def query_sales_data(product_name: str, year: int = 2025) -> tuple:
    """查詢指定商品的年度銷售數據。

    Args:
        product_name: 商品名稱
        year: 查詢年份
    """

    # 模擬從資料庫查詢
    sales_data = {
        "months": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "revenue": [120000, 135000, 142000, 128000, 155000, 168000],
        "units_sold": [240, 270, 284, 256, 310, 336],
        "product": product_name,
        "year": year,
        "total_revenue": 848000,
        "total_units": 1696
    }

    # content: 給 LLM 的簡要摘要
    content = (
        f"{year}年「{product_name}」銷售摘要：\n"
        f"上半年總營收：NT${sales_data['total_revenue']:,}\n"
        f"上半年總銷量：{sales_data['total_units']} 件\n"
        f"月均營收：NT${sales_data['total_revenue'] // 6:,}"
    )

    # artifact: 給使用者或下游程式的完整資料
    artifact = sales_data
    return content, artifact

# 測試直接呼叫
result = query_sales_data.invoke({"product_name": "防曬乳", "year": 2025})

print("=== 回傳結果 ===")
print(result)
