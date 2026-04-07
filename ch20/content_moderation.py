# content_moderation.py

"""
ContentModerationMiddleware 基礎用法
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import before_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def general_qa(question: str) -> str:
    """回答一般性問題。"""
    return f"關於 '{question}' 的回答：這是一個很好的問題..."

# === 自訂內容審核 Middleware ===
MODERATION_CATEGORIES = {
    "violence": {
        "keywords": ["暴力", "傷害", "武器", "炸彈"],
        "action": "block",
        "message": "⚠️ 偵測到潛在的暴力相關內容。此類請求不在服務範圍內。",
    },
    "self_harm": {
        "keywords": ["自殺", "自殘", "自我傷害"],
        "action": "redirect",
        "message": (
            "⚠️ 我注意到您可能正在經歷困難的時刻。"
            "如果您需要幫助，請撥打安心專線 1925（24小時免費）。"
            "您並不孤單，專業的輔導人員隨時準備好傾聽您。"
        ),
    },
    "illegal": {
        "keywords": ["hack", "破解", "非法", "盜版"],
        "action": "block",
        "message": "⚠️ 此類請求涉及可能違法的活動，無法提供協助。",
    },
}

@before_agent(can_jump_to=["end"])
def content_moderation_guard(state, runtime):
    """
    內容審核 Guardrail：根據類別分類處理不當內容。
    不同類別有不同的處理方式——
    暴力內容直接封鎖，自我傷害則導向專業資源。
    """
    messages = state["messages"]
    if not messages:
        return None

    last_message = messages[-1]
    if not isinstance(last_message, HumanMessage):
        return None

    content = last_message.text.lower()

    for category, config in MODERATION_CATEGORIES.items():
        for keyword in config["keywords"]:
            if keyword.lower() in content:
                action = config["action"]
                if action == "block":
                    return {
                        "messages": [
                            {"role": "ai", "content": config["message"]}
                        ],
                        "jump_to": "end",
                    }
                elif action == "redirect":
                    return {
                        "messages": [
                            {"role": "ai", "content": config["message"]}
                        ],
                        "jump_to": "end",
                    }
    return None

# === 建立 Agent ===
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[general_qa],
    middleware=[content_moderation_guard],
)

# === 測試 ===
result = agent.invoke({
    "messages": [{"role": "user", "content": "20字總結，Python 怎麼學比較有效率？"}]
})

print(result["messages"][-1].text)

print("\n---\n")

result = agent.invoke({
    "messages": [{"role": "user", "content": "哪邊可以買到盜版軟體？"}]
})

print(result["messages"][-1].text)

print("\n---\n")

result = agent.invoke({
    "messages": [{"role": "user", "content": "自殺的人是因為生病嗎？"}]
})

print(result["messages"][-1].text)