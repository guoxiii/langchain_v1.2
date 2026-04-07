# src/test_multilingual.py
# 測試多語言 Middleware

from langchain.agents import create_agent
from src.multilingual import MultilingualMiddleware, MergeableChat
from src.recommendation import search_products_by_description

agent = create_agent(
    model=MergeableChat(model="claude-sonnet-4-6"),
    tools=[search_products_by_description],
    system_prompt="你是電商保養品顧問 AI。",
    middleware=[MultilingualMiddleware()],
)

# 中文查詢
result_zh = agent.invoke({
    "messages": [{"role": "user", "content": "有沒有適合油性肌膚的保養品？"}]
})

print("中文回覆：", result_zh["messages"][-1].content)

# 英文查詢 — 同一個 Agent 會自動切換語言
result_en = agent.invoke({
    "messages": [{"role": "user", "content": "Do you have any products for oily skin?"}]
})

print("English reply:", result_en["messages"][-1].content)