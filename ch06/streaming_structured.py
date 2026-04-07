# ch06/streaming_structured.py

"""串流模式下取得結構化輸出"""
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

class Summary(BaseModel):
    """文章摘要"""
    title: str = Field(description="文章標題")
    key_points: list[str] = Field(description="重點列表")
    word_count: int = Field(description="估計字數")

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(Summary),
)

# 使用 stream 取得串流結果
for chunk in agent.stream({
    "messages": [{
        "role": "user",
        "content": "請摘要：LangChain v1 引入了 Middleware 和 create_agent 等核心功能..."
    }]
}):

    # 每個 chunk 是一個 (node_name, state_update) 的元組
    for node_name, state_update in chunk.items():
        if "structured_response" in state_update:
            summary = state_update["structured_response"]
            print(f"標題：{summary.title}")
            print(f"重點：{summary.key_points}")
            print(f"估計字數：{summary.word_count}")
