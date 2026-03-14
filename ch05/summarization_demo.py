# 檔案：ch05/summarization_demo.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash",
            trigger=("messages", 8),    # 為了 Demo，設低一點
            keep=("messages", 4),       # 保留最近 4 則
            summary_prefix="[對話摘要] ",  # 摘要訊息的前綴
        ),
    ],
    checkpointer=InMemorySaver(),
)

thread_config = {"configurable": {"thread_id": "summarize-demo"}}

# 模擬多輪對話
conversations = [
    "你好，我想規劃一趟日本旅行",
    "我打算去東京和京都",
    "大概五天四夜",
    "預算大約台幣五萬",
    "有推薦的景點嗎？",
    "那美食呢？有推薦的餐廳嗎？",
    "交通方面，我應該買 JR Pass 嗎？",
    "最後幫我總結一下行程規劃",
]

for i, msg in enumerate(conversations, 1):
    print(f"\n--- 第 {i} 輪對話 ---")
    print(f"👤 使用者：{msg}")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": msg}]},
        config=thread_config,
    )

    reply = result["messages"][-1].content
    print(f"🤖 Agent：{reply[:100]}...")

    # 顯示目前的訊息數量
    msg_count = len(result["messages"])
    print(f"   📊 目前訊息數：{msg_count}")
