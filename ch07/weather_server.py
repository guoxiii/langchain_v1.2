# weather_server.py
"""一個模擬天氣查詢的 MCP Server（HTTP 傳輸）"""
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Weather")

@mcp.tool()
def get_weather(city: str) -> dict:
    """查詢指定城市的天氣資訊。

    Args:
        city: 城市名稱（例如：Taipei、Tokyo、New York）

    Returns:
        包含溫度、天氣狀況、濕度的字典
    """

    # 這裡用模擬資料，實際專案中你會呼叫真正的天氣 API
    weather_data = {
        "Taipei": {"temperature": 28, "condition": "多雲", "humidity": 75},
        "Tokyo": {"temperature": 22, "condition": "晴天", "humidity": 55},
        "New York": {"temperature": 15, "condition": "陰天", "humidity": 65},
    }

    if city in weather_data:
        data = weather_data[city]

        return {
            "city": city,
            "temperature": data["temperature"],
            "condition": data["condition"],
            "humidity": data["humidity"],
            "unit": "°C",
        }
    else:
        return {"error": f"找不到城市 '{city}' 的天氣資料"}

@mcp.tool()
def get_forecast(city: str, days: int = 3) -> dict:
    """查詢指定城市的未來天氣預報。

    Args:
        city: 城市名稱
        days: 預報天數（預設 3 天，最多 7 天）

    Returns:
        包含每日預報的字典
    """

    if days > 7:
        days = 7

    # 模擬預報資料
    forecast = []
    base_temp = 25

    for i in range(days):
        forecast.append({
            "day": f"第 {i + 1} 天",
            "high": base_temp + i,
            "low": base_temp - 5 + i,
            "condition": "晴天" if i % 2 == 0 else "多雲",
        })

    return {"city": city, "forecast": forecast}


# 用 HTTP 傳輸方式啟動 Server（預設在 http://localhost:8000/mcp）
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
