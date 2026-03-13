# ch06/tool_strategy_with_tools.py

"""ToolStrategy 搭配真正的工具"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool

load_dotenv()

# 定義一個真正的工具
@tool
def search_movie_info(movie_name: str) -> str:
    """搜尋電影資訊（模擬）"""
    # 實際應用中，這裡會呼叫電影資料庫 API
    return f"《{movie_name}》是 2017 年上映的中國電影，導演韓寒，豆瓣評分 6.8。"
# 定義結構化輸出格式
class MovieAnalysis(BaseModel):
    """電影分析結果"""
    title: str = Field(description="電影名稱")
    director: str = Field(description="導演")
    year: int = Field(description="上映年份")
    douban_score: float = Field(description="豆瓣評分")
    recommendation: str = Field(description="推薦原因")

# 同時設定 tools 和 response_format
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[search_movie_info],                    # 真正的工具
    response_format=ToolStrategy(MovieAnalysis),   # 結構化輸出
    system_prompt="你是一個電影分析助手。先用工具查詢電影資訊，再給出結構化的分析結果。",
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "幫我查一下《乘風破浪》這部電影並給出分析"
    }]
})

# 工具呼叫的結果在 messages 裡
for msg in result["messages"]:
    print(f"[{type(msg).__name__}] {str(msg.content)[:80]}")

# 結構化的最終結果在 structured_response 裡
analysis = result["structured_response"]

print(f"\n=== 結構化分析結果 ===")
print(f"電影：{analysis.title}（{analysis.year}）")
print(f"導演：{analysis.director}")
print(f"豆瓣：{analysis.douban_score}")
print(f"推薦：{analysis.recommendation}")
