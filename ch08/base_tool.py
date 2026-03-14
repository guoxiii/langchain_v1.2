# ch08/base_tool.py
from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import httpx

# 1. 定義輸入 Schema
class WeatherInput(BaseModel):
    """天氣查詢的輸入參數。"""
    city: str = Field(description="城市名稱，例如 'Taipei' 或 'Tokyo'")
    units: str = Field(
        default="metric",
        description="溫度單位：metric（攝氏）或 imperial（華氏）"
    )

# 2. 定義工具類別
class WeatherTool(BaseTool):
    """查詢指定城市的目前天氣狀況。"""
    # 工具基本屬性
    name: str = "get_weather"
    description: str = (
        "查詢指定城市的即時天氣資訊，包含溫度、濕度和天氣描述。"
        "請提供城市的英文名稱。"
    )
    args_schema: Type[BaseModel] = WeatherInput

    # 自訂實例變數
    api_key: str = ""
    base_url: str = "https://api.openweathermap.org/data/2.5/weather"

    def _run(self, city: str, units: str = "metric") -> str:
        """同步執行工具（必須實作）。"""
        try:
            response = httpx.get(
                self.base_url,
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": units,
                    "lang": "zh_tw"
                },
                timeout=10.0
            )

            response.raise_for_status()
            data = response.json()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            desc = data["weather"][0]["description"]
            unit_symbol = "°C" if units == "metric" else "°F"

            return (
                f"{city} 目前天氣：{desc}\n"
                f"溫度：{temp}{unit_symbol}\n"
                f"濕度：{humidity}%"
            )

        except httpx.HTTPStatusError as e:
            return f"查詢失敗：HTTP {e.response.status_code}"
        except Exception as e:
            return f"查詢失敗：{e}"

    async def _arun(self, city: str, units: str = "metric") -> str:
        """非同步執行工具（選擇性實作，但強烈建議）。"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": city,
                        "appid": self.api_key,
                        "units": units,
                        "lang": "zh_tw"
                    },
                    timeout=10.0
                )

                response.raise_for_status()
                data = response.json()
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                desc = data["weather"][0]["description"]
                unit_symbol = "°C" if units == "metric" else "°F"

                return (
                    f"{city} 目前天氣：{desc}\n"
                    f"溫度：{temp}{unit_symbol}\n"
                    f"濕度：{humidity}%"
                )
        except httpx.HTTPStatusError as e:
            return f"查詢失敗：HTTP {e.response.status_code}"
        except Exception as e:
            return f"查詢失敗：{e}"

# 3. 建立工具實例
import os

weather_tool = WeatherTool(api_key=os.getenv("OPENWEATHER_API_KEY", "demo_key"))

# 查看工具屬性
print(f"名稱：{weather_tool.name}")
print(f"描述：{weather_tool.description}")
print(f"參數：{weather_tool.args}")
