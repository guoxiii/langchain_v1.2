# ch03/streaming_usage.py

"""
示範在串流中取得 Token 使用量
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")
full_response = ""
usage_metadata = None

for chunk in model.stream("什麼是機器學習？請簡短回答。"):
    full_response += chunk.content

    # Token 使用量通常在最後一個 chunk
    if chunk.usage_metadata:
        usage_metadata = chunk.usage_metadata

print(f"完整回應：{full_response}")
print()

if usage_metadata:
    print(f"Token 使用量：")
    print(f"  輸入 Token：{usage_metadata.get('input_tokens', 'N/A')}")
    print(f"  輸出 Token：{usage_metadata.get('output_tokens', 'N/A')}")
    print(f"  合計 Token：{usage_metadata.get('total_tokens', 'N/A')}")
