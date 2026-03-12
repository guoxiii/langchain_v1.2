# ch03/content_blocks_reasoning.py

"""
示範解析包含 reasoning 的 Content Blocks
（需要支援思考功能的模型，例如 Claude）
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# Claude 支援 extended thinking
model = init_chat_model(
    "anthropic:claude-sonnet-4-6",
    thinking={"type": "enabled", "budget_tokens": 5000}
)

response = model.invoke("9.11 和 9.8，哪個比較大？請仔細思考。")

# 使用 content_blocks 解析回應
for block in response.content_blocks:
    if block["type"] == "reasoning":
        print("【模型的思考過程】")
        print(block.get("reasoning", "（思考內容）"))
        print()
    elif block["type"] == "text":
        print("【最終回答】")
        print(block["text"])
