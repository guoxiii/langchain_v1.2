# ch03/content_blocks_basic.py

"""
示範 Content Blocks 的基本用法
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")
response = model.invoke("用一句話解釋量子力學。")

# .content —— 原始內容（通常是純文字字串）
print("【.content】")
print(response.content)
print(f"類型：{type(response.content)}")
print()

# .content_blocks —— 標準化的內容區塊列表
print("【.content_blocks】")

for block in response.content_blocks:
    print(f"  區塊類型：{block['type']}")

    if block["type"] == "text":
        print(f"  文字內容：{block['text']}")
