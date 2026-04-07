# src/my_agent/agent.py

"""使用工廠函式的 Agent -- 支援執行時期動態配置"""
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """搜尋網路上的最新資訊。"""
    return f"搜尋結果：關於 '{query}' 的最新資訊..."

def make_graph(config: dict):
    """
    工廠函式：根據配置動態建立 Agent。
    LangGraph Platform 會在每次需要 Graph 時呼叫這個函式。
    """
    # 從 config 中讀取可配置的參數
    configurable = config.get("configurable", {})
    model_name = configurable.get("model", "anthropic:claude-sonnet-4-6")

    system_prompt = configurable.get(
        "system_prompt",
        "你是一位友善的 AI 助理，請用繁體中文回答。"
    )

    model = init_chat_model(model_name)

    return create_agent(
        model=model,
        tools=[web_search],
        system_prompt=system_prompt,
    )

# 匯出工廠函式
graph = make_graph