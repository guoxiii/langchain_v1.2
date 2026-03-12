# ch03/profile_adaptive.py

"""
示範根據 Model Profile 自動調整行為
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

def smart_invoke(model_string: str, question: str):
    """根據模型能力自動選擇最佳呼叫方式"""
    model = init_chat_model(model_string)
    profile = model.profile

    

    # 如果模型支援結構化輸出，就使用它
    if profile.get("structured_output"):
        print(f"  ✅ {model_string} 支援 Structured Output")
    else:
        print(f"  ❌ {model_string} 不支援 Structured Output")    

    # 如果模型支援 Tool Calling，就可以使用 Agent

    if profile.get("tool_calling"):
        print(f"  ✅ {model_string} 支援 Tool Calling（可作為 Agent）")
    else:
        print(f"  ❌ {model_string} 不支援 Tool Calling")    

    # 檢查上下文窗口大小
    max_input = profile.get("max_input_tokens")

    if max_input:
        print(f"  📏 最大輸入 Token：{max_input:,}")    

    response = model.invoke(question)
    return response.content

# 比較不同模型的能力
for model_str in ["google_genai:gemini-2.5-flash", "anthropic:claude-sonnet-4-6"]:
    print(f"\n【{model_str}】")
    result = smart_invoke(model_str, "Hello!")
    print(f"  回應：{result[:50]}...")
