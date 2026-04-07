# ch03/switch_models.py
"""
示範如何在不同模型供應商之間切換
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

question = "請用一句話解釋什麼是人工智慧。"

# --- 使用 Gemini ---
gemini = init_chat_model("google_genai:gemini-2.5-flash")
response_gemini = gemini.invoke(question)

print(f"Gemini 說：{response_gemini.content}")

# --- 使用 Claude ---
claude = init_chat_model("anthropic:claude-sonnet-4-6")
response_claude = claude.invoke(question)

print(f"Claude 說：{response_claude.content}")
