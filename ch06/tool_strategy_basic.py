# ch06/tool_strategy_basic.py

"""ToolStrategy 基本範例"""
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

# 步驟一：定義你要的輸出格式（Schema）
class MovieReview(BaseModel):
    """電影評論的結構化格式"""
    title: str = Field(description="電影名稱")
    rating: int = Field(description="評分（1-10 分）")
    genre: str = Field(description="電影類型")
    pros: list[str] = Field(description="優點列表")
    cons: list[str] = Field(description="缺點列表")
    one_line_summary: str = Field(description="一句話總結")

# 步驟二：使用 ToolStrategy 包裝 Schema
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(MovieReview),
)

# 步驟三：呼叫 Agent
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "請分析電影《乘風破浪》：劇情溫馨但節奏稍慢，演員表現出色，適合文藝片愛好者。"
    }]
})

# 步驟四：取得結構化結果
review = result["structured_response"]

print(f"電影名稱：{review.title}")
print(f"評分：{review.rating}/10")
print(f"類型：{review.genre}")
print(f"優點：{', '.join(review.pros)}")
print(f"缺點：{', '.join(review.cons)}")
print(f"一句話總結：{review.one_line_summary}")
