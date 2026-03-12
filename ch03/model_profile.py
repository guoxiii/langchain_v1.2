# ch03/model_profile.py

"""
示範 Model Profiles 的使用方式
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# 初始化模型
model = init_chat_model("google_genai:gemini-2.5-flash")

# 查詢模型的 Profile
profile = model.profile

print("【模型能力一覽】")
print(f"  支援 Tool Calling：{profile.get('tool_calling', '未知')}")
print(f"  支援 Structured Output：{profile.get('structured_output', '未知')}")
print(f"  最大輸入 Token 數：{profile.get('max_input_tokens', '未知')}")
print(f"  最大輸出 Token 數：{profile.get('max_output_tokens', '未知')}")
