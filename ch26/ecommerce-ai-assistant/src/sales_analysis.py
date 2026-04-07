# src/sales_analysis.py

"""
銷售數據分析模組
使用 Deep Agent 進行多步驟數據分析
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from deepagents import create_deep_agent
import pandas as pd
import json

# ============================================================
# 定義數據分析專用工具
# ============================================================

@tool
def load_sales_data(file_path: str = "data/sales_data.csv") -> str:
    """
    載入銷售數據 CSV 檔案，回傳基本統計資訊。    

    Args:
        file_path: CSV 檔案路徑   

    Returns:
        數據概覽的 JSON 字串，包含欄位資訊、筆數、日期範圍等
    """

    df = pd.read_csv(file_path)

    overview = {
        "total_records": len(df),
        "columns": list(df.columns),
        "date_range": {
            "start": df["date"].min(),
            "end": df["date"].max(),
        },
        "total_revenue": int(df["total_amount"].sum()),
        "total_orders": df["order_id"].nunique(),
        "unique_products": df["product_id"].nunique(),
        "unique_customers": df["customer_id"].nunique(),
        "sample_rows": df.head(5).to_dict(orient="records"),
    }

    return json.dumps(overview, ensure_ascii=False, indent=2)

@tool
def analyze_monthly_trend(file_path: str = "data/sales_data.csv") -> str:
    """
    分析月度銷售趨勢，包含每月營收、訂單量和客單價。    

    Args:
        file_path: CSV 檔案路徑    

    Returns:
        月度趨勢數據的 JSON 字串
    """

    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month").agg(
        revenue=("total_amount", "sum"),
        orders=("order_id", "nunique"),
        items_sold=("quantity", "sum"),
        avg_order_value=("total_amount", "mean"),
    ).reset_index()

    monthly["avg_order_value"] = monthly["avg_order_value"].round(0).astype(int)
    monthly["revenue"] = monthly["revenue"].astype(int)

    return json.dumps(
        monthly.to_dict(orient="records"),
        ensure_ascii=False,
        indent=2,
    )

@tool
def analyze_product_performance(file_path: str = "data/sales_data.csv") -> str:
    """
    分析各商品的銷售表現，包含銷量、營收、排名。    

    Args:
        file_path: CSV 檔案路徑    

    Returns:
        商品表現數據的 JSON 字串
    """

    df = pd.read_csv(file_path)

    product_stats = df.groupby(["product_id", "product_name"]).agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("total_amount", "sum"),
        order_count=("order_id", "nunique"),
        avg_unit_price=("unit_price", "mean"),
    ).reset_index()

    product_stats = product_stats.sort_values("total_revenue", ascending=False)
    product_stats["revenue_rank"] = range(1, len(product_stats) + 1)
    product_stats["avg_unit_price"] = product_stats["avg_unit_price"].round(0).astype(int)
    product_stats["total_revenue"] = product_stats["total_revenue"].astype(int)

    return json.dumps(
        product_stats.to_dict(orient="records"),
        ensure_ascii=False,
        indent=2,
    )

@tool
def analyze_channel_performance(file_path: str = "data/sales_data.csv") -> str:
    """
    分析各銷售通路的表現。    

    Args:
        file_path: CSV 檔案路徑    

    Returns:
        通路表現數據的 JSON 字串
    """

    df = pd.read_csv(file_path)

    channel_stats = df.groupby("channel").agg(
        total_revenue=("total_amount", "sum"),
        order_count=("order_id", "nunique"),
        unique_customers=("customer_id", "nunique"),
        avg_order_value=("total_amount", "mean"),
    ).reset_index()

    channel_stats = channel_stats.sort_values("total_revenue", ascending=False)
    channel_stats["avg_order_value"] = channel_stats["avg_order_value"].round(0).astype(int)
    channel_stats["total_revenue"] = channel_stats["total_revenue"].astype(int)
    total_revenue = channel_stats["total_revenue"].sum()

    channel_stats["revenue_share_pct"] = (
        channel_stats["total_revenue"] / total_revenue * 100
    ).round(1)

    return json.dumps(
        channel_stats.to_dict(orient="records"),
        ensure_ascii=False,
        indent=2,
    )

@tool
def analyze_regional_performance(file_path: str = "data/sales_data.csv") -> str:
    """
    分析各地區的銷售表現。    

    Args:
        file_path: CSV 檔案路徑    

    Returns:
        地區表現數據的 JSON 字串
    """

    df = pd.read_csv(file_path)

    region_stats = df.groupby("region").agg(
        total_revenue=("total_amount", "sum"),
        order_count=("order_id", "nunique"),
        top_product=("product_name", lambda x: x.value_counts().index[0]),
    ).reset_index()

    region_stats = region_stats.sort_values("total_revenue", ascending=False)
    region_stats["total_revenue"] = region_stats["total_revenue"].astype(int)

    return json.dumps(
        region_stats.to_dict(orient="records"),
        ensure_ascii=False,
        indent=2,
    )

# ============================================================
# 建立銷售分析 Deep Agent
# ============================================================

def create_sales_analysis_agent():
    """
    建立銷售數據分析 Deep Agent。    

    為什麼用 Deep Agent 而不是普通 Agent？
    因為銷售分析通常需要多步驟的探索性分析：
    1. 先看整體概況
    2. 發現異常或趨勢
    3. 深入鑽研特定維度
    4. 交叉比對
    5. 產出結論與建議    

    Deep Agent 的 TodoList 功能讓它能像真正的分析師一樣，
    規劃分析步驟並逐一執行。
    """
    analysis_tools = [
        load_sales_data,
        analyze_monthly_trend,
        analyze_product_performance,
        analyze_channel_performance,
        analyze_regional_performance,
    ]

    model = init_chat_model("anthropic:claude-sonnet-4-6")

    agent = create_deep_agent(
        model=model,
        tools=analysis_tools,
        system_prompt="""你是一位資深的電商數據分析師。你的任務是分析銷售數據並產出有洞察力的分析報告。

分析時請遵循以下步驟：
1. 先載入數據並了解整體概況
2. 分析月度趨勢，找出成長或衰退的月份
3. 分析各商品的表現，找出明星商品和需要改善的商品
4. 分析各通路的貢獻度
5. 分析各地區的差異
6. 綜合以上分析，提出具體的商業建議

分析報告格式要求：
- 使用清楚的數據支撐每個觀點
- 提供具體且可執行的建議
- 用淺顯的語言，避免過多統計術語
- 報告最後附上「關鍵發現摘要」
""",
    )

    return agent

# ============================================================
# 執行分析
# ============================================================

if __name__ == "__main__":
    agent = create_sales_analysis_agent()

    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "請分析我們 2025 年的完整銷售數據，重點關注：1) 哪些商品表現最好？2) 各通路的營收佔比如何？3) 有沒有明顯的季節性趨勢？最後請給我三條具體的商業建議。",
        }]
    })

    last_message = result["messages"][-1]

    print(last_message.content)
