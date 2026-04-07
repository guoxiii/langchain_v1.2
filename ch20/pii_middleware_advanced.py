# pii_middleware_advanced.py

"""
PIIMiddleware 進階應用：多類型偵測 + 自定義偵測器
"""

from dotenv import load_dotenv
load_dotenv()

import re
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_core.tools import tool

@tool
def save_customer_note(note: str) -> str:
    """儲存客戶備註。"""
    return f"備註已儲存：{note}"

@tool
def lookup_customer(name: str) -> str:
    """查詢客戶資料。"""
    return f"客戶 {name} 的資料：VIP 會員，最近訂單 #12345"

# === 自定義偵測器：台灣身分證字號 ===
def detect_tw_national_id(content: str) -> list[dict[str, str | int]]:
    """
    偵測台灣身分證字號格式：一個英文字母 + 九個數字。
    例如：A123456789    

    這是自定義偵測器的完整寫法。偵測器函式必須：
    1. 接收一個 str 參數（要檢查的內容）
    2. 回傳 list[dict]，每個 dict 包含 text、start、end
    """

    matches = []

    # 台灣身分證格式：一個大寫英文字母 + 9 個數字
    pattern = r"\b[A-Z][12]\d{8}\b"    

    for match in re.finditer(pattern, content):
        candidate = match.group(0)
        # 簡易驗證：首字母 A-Z 對應不同縣市
        first_letter = candidate[0]

        if first_letter.isalpha() and first_letter.upper() in "ABCDEFGHJKLMNPQRSTUVWXYZ":
            matches.append({
                "text": candidate,
                "start": match.start(),
                "end": match.end(),
            })

    

    return matches

# === 自定義偵測器：台灣手機號碼 ===
def detect_tw_phone(content: str) -> list[dict[str, str | int]]:
    """偵測台灣手機號碼格式：09xx-xxx-xxx 或 09xxxxxxxx"""
    matches = []
    pattern = r"\b09\d{2}[-\s]?\d{3}[-\s]?\d{3}\b"   

    for match in re.finditer(pattern, content):
        matches.append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
        })    

    return matches

# === 建立具備完整 PII 防護的 Agent ===
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[save_customer_note, lookup_customer],
    middleware=[
        # 內建類型：Email 偵測 + 遮蔽
        PIIMiddleware("email", strategy="redact", apply_to_input=True),        

        # 內建類型：信用卡號碼 + 部分遮蔽（保留後四碼）
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),        

        # 內建類型：IP 位址 + 雜湊替代
        PIIMiddleware("ip", strategy="hash"),        

        # 自定義類型：台灣身分證字號 + 直接阻擋
        PIIMiddleware(
            "tw_national_id",
            detector=detect_tw_national_id,
            strategy="block",
        ),

        

        # 自定義類型：台灣手機號碼 + 遮蔽
        PIIMiddleware(
            "tw_phone",
            detector=detect_tw_phone,
            strategy="redact",
        ),        

        # 使用 Regex 字串快速定義：API Key 格式
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32,}",
            strategy="block",
        ),
    ],
)

# === 測試 ===
# 測試 Email 遮蔽
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "請幫我記錄客戶資料，他的 email 是 john@example.com"
    }]
})

print("📧 Email 遮蔽：", result["messages"][-1].text)

# 測試手機號碼遮蔽
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "客戶的聯絡電話是 0912-345-678，請記錄下來"
    }]
})

print("📱 手機遮蔽：", result["messages"][-1].text)

# 測試身分證字號攔截（block 策略會拋出例外）
try:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": "客戶身分證字號是 A123456789"
        }]
    })

except Exception as e:
    print(f"🆔 身分證阻擋：{e}")
