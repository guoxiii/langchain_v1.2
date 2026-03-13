# ch06/error_handling.py

"""結構化輸出的錯誤處理完整範例"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

class StrictScore(BaseModel):
    """嚴格的評分格式"""
    item_name: str = Field(description="被評分的項目名稱")

    score: int = Field(
        description="分數，必須是 1 到 5 之間的整數",
        ge=1,
        le=5,
    )

    comment: str = Field(
        description="評語，至少 10 個字",
        min_length=10,
    )

def my_error_handler(error: Exception) -> str:
    """自訂的友善錯誤提示"""
    error_msg = str(error)

    if "score" in error_msg:
        return "分數必須介於 1 到 5 之間（整數）。請修正後重新回答。"
    elif "comment" in error_msg:
        return "評語太短了，請至少寫 10 個字。"
    else:
        return f"格式有誤，請依照 Schema 重新填寫。錯誤訊息：{error_msg}"

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(
        schema=StrictScore,
        handle_errors=my_error_handler,
    ),
)

# 故意給一個容易讓 LLM 填錯的輸入
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "幫我評分：蘋果手機，我覺得 100 分！超讚！"
    }]
})

score = result["structured_response"]

print(f"項目：{score.item_name}")
print(f"分數：{score.score}/5")
print(f"評語：{score.comment}")
