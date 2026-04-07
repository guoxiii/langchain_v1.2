# 檔案名稱：llm_node.py

"""
在 LangGraph Node 中使用 LLM
"""

from dotenv import load_dotenv
load_dotenv()

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

# 初始化 LLM
llm = init_chat_model("google_genai:gemini-2.5-flash")


class QAState(TypedDict):
    question: str
    answer: str

def ask_llm(state: QAState) -> dict:
    """使用 LLM 回答問題"""
    response = llm.invoke([
        HumanMessage(content=state["question"])
    ])

    return {"answer": response.content}


# 建立並執行圖
graph_builder = StateGraph(QAState)
graph_builder.add_node("ask", ask_llm)
graph_builder.add_edge(START, "ask")
graph_builder.add_edge("ask", END)
graph = graph_builder.compile()

result = graph.invoke({"question": "用一句話解釋什麼是 Python？"})

print(f"問題：{result['question']}")
print(f"回答：{result['answer']}")
