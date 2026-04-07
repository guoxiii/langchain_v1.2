"""
檔案：fallback_demo.py
ModelFallbackMiddleware：主模型失敗時自動切換備用模型
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """搜尋網路"""
    return f"搜尋 '{query}' 的結果...LangChain 最新消息：LangChain 1.2 發布了！"

agent = create_agent(
    model="google_genai:gemini-2.5-pro",   # 主要模型
    tools=[search_web],
    middleware=[
        ModelFallbackMiddleware(
            "anthropic:claude-sonnet-4-6",      # 備援模型
        ),
    ],
)

result = agent.invoke({"messages": [{"role": "user", "content": "搜尋 LangChain 最新消息"}]})
print(result["messages"][-1].content)

# 執行時，如果 gemini-2.5-pro 失敗：
# 1. 嘗試 gemini-2.5-flash
# 2. 如果還是失敗，嘗試 claude-sonnet-4-6
# 3. 全部失敗才回傳錯誤
