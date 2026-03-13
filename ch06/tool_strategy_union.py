# ch06/tool_strategy_union.py

"""ToolStrategy 的 Union Types — 多種 Schema 二選一"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

# 定義多種輸出格式
class ContactInfo(BaseModel):
    """聯絡資訊"""
    name: str = Field(description="姓名")
    email: str = Field(description="電子郵件")
    phone: str = Field(description="電話號碼")

class EventInfo(BaseModel):
    """活動資訊"""
    event_name: str = Field(description="活動名稱")
    date: str = Field(description="活動日期")
    location: str = Field(description="活動地點")

# 使用 Union Type：LLM 會自動選擇合適的 Schema
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(ContactInfo | EventInfo),  # Python 3.10+ 語法
)

# 測試一：輸入聯絡資訊
result1 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "從以下內容提取資訊：王小明，email: wang@example.com，手機 0912-345-678"
    }]
})

print(type(result1["structured_response"]))

# 輸出：<class '__main__.ContactInfo'>

# 測試二：輸入活動資訊
result2 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "從以下內容提取資訊：LangChain 技術分享會，3月15日，台北信義區會議中心"
    }]
})

print(type(result2["structured_response"]))

# 輸出：<class '__main__.EventInfo'>