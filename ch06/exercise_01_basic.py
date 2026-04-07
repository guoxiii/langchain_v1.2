# ch06/exercise_01_basic.py

"""練習一：基礎結構化輸出"""
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from langchain.agents import create_agent

load_dotenv()

# ---------- 定義 Schema ----------
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class ReviewAnalysis(BaseModel):
    """產品評論分析結果"""
    product_name: str = Field(description="被評論的產品名稱")
    sentiment: Sentiment = Field(description="整體情緒傾向")

    score: float = Field(
        description="情緒分數，0.0 到 1.0，越高越正面",
        ge=0.0,
        le=1.0,
    )

    pros: list[str] = Field(description="評論中提到的優點")
    cons: list[str] = Field(description="評論中提到的缺點")
    summary: str = Field(description="50 字以內的摘要")
    purchase_recommended: bool = Field(description="是否推薦購買")

# ---------- 建立 Agent ----------
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ReviewAnalysis,  # 直接傳入 Schema，自動選策略
    system_prompt=(
        "你是一個專業的產品評論分析師。"
        "請仔細閱讀使用者提供的評論，並按照指定格式回傳分析結果。"
        "情緒分數請盡量精確，摘要請控制在 50 字以內。"
    ),
)

# ---------- 測試 ----------
reviews = [
    "這台筆電真的太棒了！螢幕漂亮、鍵盤手感好、電池續航也很讚。唯一缺點就是稍微重了一點，帶出門有點累。整體來說非常滿意，推薦給需要高效能筆電的朋友！",
    "說實話，這個耳機讓我很失望。音質普通，降噪效果差，而且戴久了耳朵會痛。唯一的優點是外型還不錯，但這個價格買到這種品質，真的不值得。",
    "對這款手機的感覺很矛盾。拍照功能超級強大，夜拍效果驚人，但是電池續航實在太差了，重度使用撐不過半天。系統偶爾也會卡頓。算是有優有缺吧。",
]

for i, review in enumerate(reviews, 1):
    print(f"\n{'='*60}")
    print(f"評論 {i}：{review[:30]}...")
    print(f"{'='*60}")

    result = agent.invoke({
        "messages": [{"role": "user", "content": review}]
    })

    analysis = result["structured_response"]

    print(f"產品：{analysis.product_name}")
    print(f"情緒：{analysis.sentiment.value}（分數：{analysis.score}）")
    print(f"優點：{', '.join(analysis.pros)}")
    print(f"缺點：{', '.join(analysis.cons)}")
    print(f"摘要：{analysis.summary}")
    print(f"推薦：{'✅ 推薦' if analysis.purchase_recommended else '❌ 不推薦'}")
