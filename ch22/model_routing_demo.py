"""
檔案：model_routing_demo.py
根據任務複雜度動態選擇模型
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

# 定義模型層級
MODELS = {
    "fast": "google_genai:gemini-2.5-flash",    # 便宜快速
    "balanced": "anthropic:claude-sonnet-4-6",    # 品質均衡
    "powerful": "google_genai:gemini-2.5-pro",    # 強推理
}

def classify_complexity(query: str) -> str:
    """
    用最便宜的模型來判斷任務複雜度。
    這個分類本身只花不到 100 tokens。
    """

    classifier = init_chat_model(MODELS["fast"])
    result = classifier.invoke([
        SystemMessage(content=(
            "判斷以下使用者問題的複雜度。"
            "回覆 'simple'、'medium' 或 'complex'，只回覆一個詞。\n"
            "simple: 簡單問候、FAQ、是非題\n"
            "medium: 需要工具呼叫或一般分析的任務\n"
            "complex: 需要多步推理、長篇寫作、程式碼產生"
        )),
        HumanMessage(content=query),
    ])

    return result.content.strip().lower()

def get_model_for_task(query: str) -> str:
    """根據複雜度選擇模型"""
    complexity = classify_complexity(query)
    model_map = {
        "simple": "fast",
        "medium": "fast",       # Flash 對大多數任務已經夠用
        "complex": "powerful",
    }

    tier = model_map.get(complexity, "fast")
    print(f"  📊 複雜度: {complexity} → 使用模型: {tier}")
    return MODELS[tier]
