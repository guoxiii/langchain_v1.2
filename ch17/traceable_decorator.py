# ch17/traceable_decorator.py

"""使用 @traceable 裝飾器追蹤自定義函式"""

from dotenv import load_dotenv
from langsmith import traceable
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model("google_genai:gemini-2.5-flash")

@traceable(name="translate_to_english")
def translate_to_english(text: str) -> str:
    """將輸入文字翻譯成英文"""
    response = llm.invoke(f"請將以下文字翻譯成英文：{text}")
    return response.text

@traceable(name="summarize_text")
def summarize_text(text: str) -> str:
    """摘要輸入文字"""
    response = llm.invoke(f"請用一句話摘要以下內容：{text}")
    return response.text

@traceable(name="translate_and_summarize")
def translate_and_summarize(text: str) -> str:
    """先翻譯再摘要"""
    english_text = translate_to_english(text)
    summary = summarize_text(english_text)
    return summary

# 執行
result = translate_and_summarize(
    "人工智慧近年來發展迅速，特別是在自然語言處理領域，"
    "大型語言模型的出現徹底改變了人機互動的方式。"
)
print(result)
