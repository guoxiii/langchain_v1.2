"""
檔案：prompt_caching_demo.py
使用 Anthropic Prompt Caching Middleware
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware

@tool
def search_documents(query: str) -> str:
    """搜尋內部文件庫"""
    # 模擬文件搜尋
    return f"找到關於 '{query}' 的 3 篇文件..."

# Anthropic 的 Prompt Caching 可以快取 System Prompt 和長篇上下文
# 首次呼叫會寫入快取，後續呼叫直接讀取，節省大量 Token 費用
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search_documents],
    system_prompt=(
        "你是一位企業知識管理專家，熟悉公司所有內部文件。"
        "請用繁體中文回答使用者的問題，並引用相關文件。"
        # 假設這裡有一段很長的公司背景知識...
        # Prompt Caching 會在首次呼叫後快取這段內容
    ),
    middleware=[
        AnthropicPromptCachingMiddleware(),
    ],
)
