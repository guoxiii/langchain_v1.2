# pairwise_setup.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from langchain.chat_models import init_chat_model

ls_client = Client()

# ============================================================
# 定義兩個版本的 Agent（用不同的 System Prompt 模擬）
# ============================================================

model = init_chat_model("google_genai:gemini-2.5-flash")

def agent_v1(inputs: dict) -> dict:
    """V1：簡潔版 Agent"""
    prompt = "你是一個技術助手。請簡潔地回答問題。"

    response = model.invoke([
        {"role": "system", "content": prompt},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.text}

def agent_v2(inputs: dict) -> dict:
    """V2：詳細版 Agent（改良版）"""

    prompt = (
        "你是一個資深的 LangChain 技術顧問。"
        "請用清晰的結構回答問題，必要時使用列表格式。"
        "回答應包含具體的 API 名稱和使用範例。"
    )

    response = model.invoke([
        {"role": "system", "content": prompt},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.text}


# ============================================================
# 在同一個 Dataset 上執行兩組 Experiment
# ============================================================

dataset_name = "RAG-QA-Evaluation-v1"

# Experiment A：V1 Agent
results_v1 = ls_client.evaluate(
    agent_v1,
    data=dataset_name,
    experiment_prefix="Agent-V1-Concise",
    description="V1: 簡潔風格的回答",
)

# Experiment B：V2 Agent
results_v2 = ls_client.evaluate(
    agent_v2,
    data=dataset_name,
    experiment_prefix="Agent-V2-Detailed",
    description="V2: 詳細結構化的回答",
)

print("✅ 兩組 Experiment 已完成，前往 LangSmith UI 建立 Pairwise Queue")
