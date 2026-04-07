# 檔案名稱：checkpointer.py

"""
Checkpointing 示範 — 讓圖記住之前的對話
"""

from dotenv import load_dotenv
load_dotenv()

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

# 初始化 LLM
llm = init_chat_model("google_genai:gemini-2.5-flash")

def chatbot(state: MessagesState) -> dict:
    """簡單的聊天節點"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 建立圖
graph_builder = StateGraph(MessagesState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 關鍵：建立 checkpointer 並傳入 compile()
checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

# 使用 thread_id 來區分不同的對話
config = {"configurable": {"thread_id": "conversation-001"}}

# 第一輪對話
result1 = graph.invoke(
    {"messages": [HumanMessage(content="你好！我叫小明。")]},
    config=config,
)

print("第一輪回覆：", result1["messages"][-1].content)

# 第二輪對話 — 同一個 thread_id，Agent 應該記得小明
result2 = graph.invoke(
    {"messages": [HumanMessage(content="你還記得我的名字嗎？")]},
    config=config,
)

print("第二輪回覆：", result2["messages"][-1].content)
# 不同的 thread_id — 全新的對話，Agent 不會記得小明

config2 = {"configurable": {"thread_id": "conversation-002"}}

result3 = graph.invoke(
    {"messages": [HumanMessage(content="你知道我是誰嗎？")]},
    config=config2,
)

print("新對話回覆：", result3["messages"][-1].content)
