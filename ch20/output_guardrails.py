# output_guardrails.py

"""
Output Guardrails：使用 after_model 驗證 LLM 輸出
"""

from dotenv import load_dotenv
load_dotenv()

import re
from langchain.agents import create_agent
from langchain.agents.middleware import after_model
from langchain_core.tools import tool
from langchain_core.messages import AIMessage

@tool
def medical_lookup(symptom: str) -> str:
    """查詢症狀相關的醫療資訊。"""
    info = {
        "頭痛": "頭痛可能由多種原因引起,包括壓力、脫水、睡眠不足等。",
        "發燒": "發燒是身體對抗感染的自然反應。體溫超過 38°C 建議就醫。",
    }
    return info.get(symptom, f"關於 '{symptom}' 的醫療資訊,請諮詢專業醫師。")

# === Output Guardrail:醫療免責聲明 ===
@after_model
def medical_disclaimer_guard(state, _runtime):
    """
    確保所有涉及醫療的回覆都附帶免責聲明。

    重點:使用原訊息的 id 讓 add_messages reducer 執行「替換」,
    而不是「追加」一則新訊息——否則 state 裡會同時存在原始回覆與
    補上免責聲明的版本,多輪對話時會浪費 token 且邏輯混亂。
    """
    messages = state["messages"]
    if not messages:
        return None

    last = messages[-1]
    content = last.text

    # 如果沒有文字內容(例如純 tool_call),跳過
    if not content:
        return None

    # 醫療相關關鍵字
    medical_keywords = [
        "症狀", "治療", "藥物", "診斷", "疾病",
        "醫生", "醫師", "處方", "用藥", "劑量",
        "手術", "檢查", "病情", "感染", "發炎",
    ]
    has_medical_content = any(k in content for k in medical_keywords)

    # 避免與 LLM 自己寫的免責聲明重複:用語意片段判斷,而非完整字串比對
    disclaimer_markers = [
        "僅供參考",
        "不構成醫療建議",
        "無法取代專業醫療",
    ]
    already_has_disclaimer = any(m in content for m in disclaimer_markers)

    if has_medical_content and not already_has_disclaimer:
        disclaimer = "\n\n⚕️ **重要提醒**:以上資訊僅供參考,不構成醫療建議。"
        return {
            "messages": [
                AIMessage(
                    content=content + disclaimer,
                    id=last.id,  # ← 關鍵:同 ID 才會被 add_messages 替換
                )
            ]
        }

    return None

# === Output Guardrail:敏感資訊洩露檢查 ===
@after_model
def output_leakage_guard(state, _runtime):
    """
    檢查 LLM 輸出是否不小心洩露了敏感資訊。
    例如:系統提示詞、內部 API 端點、資料庫連線字串等。

    即使你在 System Prompt 中告訴 LLM「不要洩露系統提示詞」,
    但 LLM 並不是 100% 可靠的——所以我們需要程式化的雙重保險。

    重點:這個護欄更需要確實「蓋掉」原訊息(而不是追加),
    否則敏感資料仍會留在 state 裡被下一輪 LLM 讀到。
    """
    messages = state["messages"]
    if not messages:
        return None

    last = messages[-1]
    content = last.text

    # 如果沒有文字內容(例如純 tool_call),跳過
    if not content:
        return None

    # 敏感模式
    sensitive_patterns = [
        # API 金鑰格式
        r"sk-[a-zA-Z0-9]{20,}",
        r"AIza[a-zA-Z0-9_-]{35}",
        # 資料庫連線字串
        r"(mysql|postgresql|mongodb):\/\/[^\s]+",
        # 內部 URL
        r"https?:\/\/internal\.[^\s]+",
        r"https?:\/\/10\.\d+\.\d+\.\d+[^\s]*",
        r"https?:\/\/192\.168\.\d+\.\d+[^\s]*",
    ]

    for pattern in sensitive_patterns:
        if re.search(pattern, content):
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "抱歉,我無法提供該資訊。"
                            "如果您有其他問題,歡迎繼續詢問。"
                        ),
                        id=last.id,  # ← 關鍵:徹底替換掉含敏感資料的原訊息
                    )
                ]
            }

    return None

# === 建立 Agent ===
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[medical_lookup],
    middleware=[
        medical_disclaimer_guard,
        output_leakage_guard,
    ],
)

# === 測試 ===
if __name__ == "__main__":
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "我最近常常頭痛,可能是什麼原因?"}
        ]
    })
    print("🏥 醫療回覆(含免責聲明):")
    print(result["messages"][-1].text)