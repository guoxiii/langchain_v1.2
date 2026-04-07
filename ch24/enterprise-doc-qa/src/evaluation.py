# evaluation.py

"""RAG 品質評估模組 — 使用 LangSmith"""

from dotenv import load_dotenv
load_dotenv()

import json
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain.chat_models import init_chat_model
from src.config import PRIMARY_MODEL

# 初始化 LangSmith Client
ls_client = Client()

def create_evaluation_dataset(
    dataset_name: str = "enterprise-doc-qa-eval",
):
    """
    建立評估資料集。
    一個好的評估資料集應該涵蓋：
    - 各種類型的問題（事實型、推理型、比較型）
    - 各種難度的問題
    - 有答案和無答案的問題
    """

    # 檢查資料集是否已存在
    try:
        dataset = ls_client.read_dataset(dataset_name=dataset_name)
        print(f"📦 資料集「{dataset_name}」已存在，跳過建立")
        return dataset
    except Exception:
        pass

    dataset = ls_client.create_dataset(
        dataset_name=dataset_name,
        description="企業文件問答系統的評估資料集",
    )

    # 範例測試案例
    test_cases = [
        {
            "inputs": {
                "question": "公司的年假政策是什麼？",
            },
            "outputs": {
                "expected_answer": (
                    "新進員工滿一年後可享有 7 天年假，"
                    "主管級以上員工享有 14 天年假。"
                ),
                "expected_source": "員工手冊",
            },
        },
        {
            "inputs": {
                "question": "產品 X 的技術規格是什麼？",
            },
            "outputs": {
                "expected_answer": (
                    "產品 X 支援 API v2.0，回應時間小於 200ms。"
                ),
                "expected_source": "產品規格書",
            },
        },
        {
            "inputs": {
                "question": "公司的辦公室在火星有分部嗎？",
            },
            "outputs": {
                "expected_answer": "根據目前文件，找不到相關資訊。",
                "expected_source": "",
            },
        },
    ]

    # 批次寫入測試案例
    ls_client.create_examples(
        inputs=[tc["inputs"] for tc in test_cases],
        outputs=[tc["outputs"] for tc in test_cases],
        dataset_id=dataset.id,
    )

    print(
        f"✅ 已建立資料集「{dataset_name}」"
        f"（{len(test_cases)} 個測試案例）"
    )

    return dataset

# ── 自定義評估器 ──
def faithfulness_evaluator(run, example) -> dict:
    """
    忠實度評估器 — 使用 LLM-as-Judge。
    檢查 Agent 的回答是否忠於檢索到的文件內容，
    有沒有「幻覺」（hallucination）。
    """
    llm = init_chat_model(PRIMARY_MODEL)
    question = example.inputs.get("question", "")
    agent_answer = run.outputs.get("answer", "")

    # 從 run 的 trace 中提取檢索到的上下文
    # （LangSmith 會自動記錄所有工具呼叫的結果）
    retrieved_context = ""

    if run.child_runs:
        for child in run.child_runs:
            if child.name == "search_documents":
                retrieved_context = str(
                    child.outputs.get("output", "")
                )
    prompt = f"""你是一位嚴格的品質評審員。請判斷以下「回答」是否忠於「檢索到的上下文」。

問題：{question}

檢索到的上下文：
{retrieved_context}

Agent 的回答：
{agent_answer}

評估標準：
- 回答中的每一個事實陳述都必須能在上下文中找到依據
- 如果回答包含上下文中沒有的資訊，那就是「不忠實」
- 如果回答正確地說「找不到相關資訊」，那是忠實的

請回答 JSON 格式：
{{"score": 0 或 1, "reason": "評判理由"}}

只輸出 JSON，不要其他文字。"""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)

        return {
            "key": "faithfulness",
            "score": result.get("score", 0),
            "comment": result.get("reason", ""),
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "key": "faithfulness",
            "score": 0,
            "comment": "評估失敗：無法解析 LLM 回應",
        }

def relevance_evaluator(run, example) -> dict:
    """
    相關性評估器 — 檢查回答是否與問題相關。
    """
    llm = init_chat_model(PRIMARY_MODEL)
    question = example.inputs.get("question", "")
    agent_answer = run.outputs.get("answer", "")

    prompt = f"""你是一位品質評審員。請判斷以下「回答」是否與「問題」相關。

問題：{question}

回答：{agent_answer}

評估標準：
- 回答是否直接回應了問題？
- 回答是否包含了問題要求的資訊？
- 如果問題問 A，回答卻在說 B，那就是不相關

請回答 JSON 格式：
{{"score": 0 或 1, "reason": "評判理由"}}

只輸出 JSON，不要其他文字。"""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)
        return {
            "key": "relevance",
            "score": result.get("score", 0),
            "comment": result.get("reason", ""),
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "key": "relevance",
            "score": 0,
            "comment": "評估失敗：無法解析 LLM 回應",
        }

def correctness_evaluator(run, example) -> dict:
    """
    正確性評估器 — 將 Agent 回答與預期答案比對。
    """

    llm = init_chat_model(PRIMARY_MODEL)
    question = example.inputs.get("question", "")
    agent_answer = run.outputs.get("answer", "")
    expected = example.outputs.get("expected_answer", "")
    prompt = f"""你是一位品質評審員。請比較「Agent 回答」與「預期答案」的一致性。

問題：{question}

Agent 回答：{agent_answer}

預期答案：{expected}

評估標準：
- Agent 回答是否包含了預期答案中的關鍵資訊？
- 允許措辭不同，但核心意思必須一致
- 如果預期答案說「找不到」，Agent 也應該表達類似意思

請回答 JSON 格式：
{{"score": 0 或 1, "reason": "評判理由"}}

只輸出 JSON，不要其他文字。"""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)
        return {
            "key": "correctness",
            "score": result.get("score", 0),
            "comment": result.get("reason", ""),
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "key": "correctness",
            "score": 0,
            "comment": "評估失敗：無法解析 LLM 回應",
        }

# ── 執行評估 ──
def run_evaluation(
    dataset_name: str = "enterprise-doc-qa-eval",
):
    """
    執行完整的 RAG 品質評估。

    這會：
    1. 載入評估資料集
    2. 對每個測試案例執行 Agent
    3. 用三個評估器打分
    4. 結果上傳到 LangSmith Dashboard
    """

    from src.citation_agent import create_doc_qa_agent, init_retriever

    # 確保 Retriever 已初始化
    init_retriever()

    agent = create_doc_qa_agent()

    def target_function(inputs: dict) -> dict:
        """評估目標函式 — 接收輸入，回傳輸出。"""
        question = inputs["question"]

        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )

        structured = result.get("structured_response")

        if structured:
            return {
                "answer": structured.answer,
                "citations": [
                    c.model_dump() for c in structured.citations
                ],
                "confidence": structured.confidence,
            }
        else:
            last_msg = result["messages"][-1]
            return {"answer": last_msg.content}

    # 執行評估
    results = evaluate(
        target_function,
        data=dataset_name,
        evaluators=[
            faithfulness_evaluator,
            relevance_evaluator,
            correctness_evaluator,
        ],
        experiment_prefix="enterprise-doc-qa",
    )

    print("\n📊 評估完成！")
    print("請前往 LangSmith Dashboard 查看詳細結果：")
    print("https://smith.langchain.com")
    return results

if __name__ == "__main__":
    # 建立評估資料集
    create_evaluation_dataset()

    # 執行評估
    run_evaluation()
