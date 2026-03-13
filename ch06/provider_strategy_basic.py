# ch06/provider_strategy_basic.py

"""ProviderStrategy 基本範例"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy

load_dotenv()

class RecipeInfo(BaseModel):
    """食譜資訊"""
    dish_name: str = Field(description="菜名")
    prep_time_minutes: int = Field(description="準備時間（分鐘）")
    difficulty: str = Field(description="難度（簡單/中等/困難）")
    ingredients: list[str] = Field(description="食材列表")
    steps: list[str] = Field(description="烹飪步驟")

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ProviderStrategy(RecipeInfo),
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "請給我一個簡單的番茄炒蛋食譜"
    }]
})

recipe = result["structured_response"]

print(f"菜名：{recipe.dish_name}")
print(f"準備時間：{recipe.prep_time_minutes} 分鐘")
print(f"難度：{recipe.difficulty}")
print(f"食材：{', '.join(recipe.ingredients)}")

for i, step in enumerate(recipe.steps, 1):
    print(f"步驟 {i}：{step}")
