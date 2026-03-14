# servers/weather_server.py

"""天氣 MCP Server — 提供天氣查詢服務（HTTP 傳輸）"""
import random
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

# 模擬天氣資料庫
WEATHER_DB = {
    "Taipei": {
        "temperature": 28,
        "condition": "多雲",
        "humidity": 75,
        "wind_speed": 12,
    },
    "Tokyo": {
        "temperature": 22,
        "condition": "晴天",
        "humidity": 55,
        "wind_speed": 8,
    },
    "New York": {
        "temperature": 15,
        "condition": "陰天",
        "humidity": 65,
        "wind_speed": 20,
    },
    "London": {
        "temperature": 10,
        "condition": "小雨",
        "humidity": 85,
        "wind_speed": 15,
    },
    "Sydney": {
        "temperature": 25,
        "condition": "晴天",
        "humidity": 50,
        "wind_speed": 10,
    },
}

@mcp.tool()
def get_weather(city: str) -> dict:
    """查詢指定城市的目前天氣。
    支援的城市：Taipei、Tokyo、New York、London、Sydney。

    Args:
        city: 城市名稱（英文）

    Returns:
        包含溫度（°C）、天氣狀況、濕度（%）、風速（km/h）的字典。
        如果城市不在資料庫中，回傳錯誤訊息。
    """

    if city in WEATHER_DB:
        data = WEATHER_DB[city]

        return {
            "city": city,
            "temperature_celsius": data["temperature"],
            "condition": data["condition"],
            "humidity_percent": data["humidity"],
            "wind_speed_kmh": data["wind_speed"],
        }
    else:
        available = ", ".join(WEATHER_DB.keys())
        return {"error": f"找不到 '{city}' 的天氣資料。可用城市：{available}"}


@mcp.tool()
def compare_weather(city1: str, city2: str) -> dict:
    """比較兩個城市的天氣。

    Args:
        city1: 第一個城市名稱
        city2: 第二個城市名稱

    Returns:
        兩個城市的天氣比較結果，包含溫度差和較暖的城市
    """

    weather1 = get_weather(city1)
    weather2 = get_weather(city2)

    if "error" in weather1 or "error" in weather2:
        errors = []

        if "error" in weather1:
            errors.append(weather1["error"])

        if "error" in weather2:
            errors.append(weather2["error"])

        return {"error": " | ".join(errors)}

    temp_diff = weather1["temperature_celsius"] - weather2["temperature_celsius"]
    warmer = city1 if temp_diff > 0 else city2

    return {
        "city1": weather1,
        "city2": weather2,
        "temperature_difference": abs(temp_diff),
        "warmer_city": warmer,
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
