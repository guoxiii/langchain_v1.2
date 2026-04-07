# ch03/usage_metadata.py

"""
示範追蹤 Token 使用量
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")
response = model.invoke("什麼是機器學習？")

print(f"回應：{response.content[:50]}...")
print()

# usage_metadata 包含 Token 使用量
if response.usage_metadata:
    print("【Token 使用量】")
    print(f"  輸入 Token：{response.usage_metadata.get('input_tokens', 'N/A')}")
    print(f"  輸出 Token：{response.usage_metadata.get('output_tokens', 'N/A')}")
    print(f"  合計 Token：{response.usage_metadata.get('total_tokens', 'N/A')}")
