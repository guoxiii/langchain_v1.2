# full_eval_pipeline.py

"""
第 18 章 實作練習:RAG 系統完整評估管線
本練習整合了 Dataset、多種 Evaluator、Experiment 比較等功能,
建立一個可重複使用的評估管線。

環境需求:
    uv add langsmith openevals langchain langchain-google-genai
"""

from dotenv import load_dotenv
load_dotenv()

import re
from langsmith import Client
from langchain.chat_models import init_chat_model
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# ============================================================
# Step 1:初始化
# ============================================================

ls_client = Client()
model = init_chat_model("google_genai:gemini-2.5-flash")

print("=" * 60)
print("📚 第 18 章實作:RAG 系統完整評估管線")
print("=" * 60)

# ============================================================
# Step 2:建立評估 Dataset
# ============================================================

DATASET_NAME = "LangChain-RAG-Eval-Pipeline"

# 清除舊資料(開發階段方便重複執行)
if ls_client.has_dataset(dataset_name=DATASET_NAME):
    old_ds = ls_client.read_dataset(dataset_name=DATASET_NAME)
    ls_client.delete_dataset(dataset_id=old_ds.id)

dataset = ls_client.create_dataset(
    dataset_name=DATASET_NAME,
    description="LangChain 技術問答的評估 Dataset — 第 18 章實作練習"
)

# 測試案例:涵蓋不同難度和面向
eval_examples = [
    {
        "inputs": {"question": "create_agent 和 create_react_agent 有什麼不同?"},
        "outputs": {
            "answer": "create_agent 是 LangChain v1 的新函式(來自 langchain.agents),"
                      "取代了已棄用的 create_react_agent。create_agent 底層使用 LangGraph "
                      "的 StateGraph,回傳 CompiledStateGraph,支援 Middleware、"
                      "Checkpointer、Structured Output 等 v1 新功能。"
        },
    },
    {
        "inputs": {"question": "如何在 LangChain v1 中實作 Human-in-the-Loop?"},
        "outputs": {
            "answer": "有兩種方式:1) 使用 Middleware 的 HumanInTheLoopMiddleware,"
                      "在 create_agent 中加入即可自動攔截工具呼叫進行人工審核。"
                      "2) 使用 LangGraph 的 interrupt_before / interrupt_after,"
                      "可在任意節點暫停並等待人工輸入。"
        },
    },
    {
        "inputs": {"question": "LangSmith 和 LangGraph 的關係是什麼?"},
        "outputs": {
            "answer": "LangSmith 是 LangChain 的可觀測性與評估平台,用於追蹤、除錯和"
                      "評估 LLM 應用。LangGraph 是用於構建有狀態工作流的框架。"
                      "兩者是互補關係:LangGraph 建立複雜的 Agent 工作流,"
                      "LangSmith 則負責監控和評估這些工作流的品質。"
        },
    },
    {
        "inputs": {"question": "什麼是 Content Blocks?"},
        "outputs": {
            "answer": "Content Blocks 是 LangChain v1 新增的跨供應商標準化輸出格式。"
                      "它將 LLM 的回應內容分類為 text、reasoning、citation、tool_call 等類型,"
                      "讓開發者不需要因為切換不同的 LLM 供應商而改變解析邏輯。"
        },
    },
    {
        "inputs": {"question": "請列出三個常用的 RAG 進階策略"},
        "outputs": {
            "answer": "常用的 RAG 進階策略包括:"
                      "1) Query Rewriting(查詢改寫):將使用者的問題重新表述,提升檢索效果。"
                      "2) HyDE(假設性文件嵌入):讓 LLM 先生成一個假設性答案,再用它來搜尋。"
                      "3) Reranking(重排序):使用 Cross-Encoder 模型對檢索結果重新排名,"
                      "提升最終送給 LLM 的文件品質。"
        },
    },
    {
        "inputs": {"question": "什麼是 CVE-2025-68664(LangGrinch)?"},
        "outputs": {
            "answer": "CVE-2025-68664(又稱 LangGrinch)是 2025 年 12 月揭露的 "
                      "langchain-core 序列化注入漏洞,CVSS 評分高達 9.3。"
                      "攻擊者可透過在 LLM 輸出中注入含有 'lc' key 的序列化資料,"
                      "觸發反序列化攻擊,竊取環境變數中的 API 金鑰。"
                      "此漏洞已在 langchain-core 1.2.5+ 中修復。"
        },
    },
]

ls_client.create_examples(
    inputs=[e["inputs"] for e in eval_examples],
    outputs=[e["outputs"] for e in eval_examples],
    dataset_id=dataset.id,
)

print(f"\n✅ Step 2:已建立 Dataset '{DATASET_NAME}',共 {len(eval_examples)} 個案例")

# ============================================================
# Step 3:定義被測試的 Agent(兩個版本)
# ============================================================

def agent_basic(inputs: dict) -> dict:
    """基礎版 Agent:最小化的 System Prompt"""

    response = model.invoke([
        {"role": "system", "content": "你是一個 AI 助手,請回答技術問題。"},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.text}

def agent_expert(inputs: dict) -> dict:
    """專家版 Agent:精心設計的 System Prompt"""
    expert_prompt = (
        "你是一位 LangChain v1.2+ 技術專家。回答規範:\n"
        "1. 使用繁體中文,專有名詞保留英文原文\n"
        "2. 先用一句話總結核心概念\n"
        "3. 提供具體的 API 名稱(包含 import 路徑)和版本號\n"
        "4. 如果涉及版本差異(v0.x → v1.x),明確說明變化\n"
        "5. 必要時提及常見陷阱或最佳實踐\n"
        "6. 保持回答在 150-300 字之間\n"
    )

    response = model.invoke([
        {"role": "system", "content": expert_prompt},
        {"role": "human", "content": inputs["question"]},
    ])

    return {"answer": response.text}

print("✅ Step 3:兩個版本的 Agent 已定義")

# ============================================================
# Step 4:定義 Evaluator 套件
# ============================================================

# 4a. LLM-as-Judge:正確性(沿用 openevals 內建英文 prompt,對事實判斷影響小)
eval_correctness = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="correctness",
)

# 4b. LLM-as-Judge:簡潔性(自訂中文版,避免英文 prompt 對中文回答過度扣分)
CHINESE_CONCISENESS_PROMPT = """你是一位技術文件審稿人,專門評估中文技術問答的「簡潔性」。

請判斷下列回答是否簡潔。評估標準:
- ✅ 簡潔:資訊密度高、沒有冗詞贅字、沒有不必要的客套話或重複說明
- ❌ 不簡潔:有大量填充詞、重複論述、過度舉例、與問題無關的延伸

重要原則:
- 中文技術回答 300-600 字屬於正常範圍,「長度本身」不應扣分
- 請只看「是否有廢話」,不要因為回答詳盡就判為不簡潔
- 列點、程式碼、必要的版本號與 API 路徑都屬於有效資訊,不算冗餘

<question>
{inputs}
</question>

<answer>
{outputs}
</answer>

請先簡短說明理由(一句話即可),最後回覆 true(簡潔)或 false(不簡潔)。"""

eval_conciseness = create_llm_as_judge(
    prompt=CHINESE_CONCISENESS_PROMPT,
    model="google_genai:gemini-2.5-flash",
    feedback_key="conciseness",
)

# 4c. 規則型:回答長度適當性(放寬門檻,加入中間層級)
def eval_length(inputs: dict, outputs: dict, **kwargs) -> dict:
    answer = str(outputs.get("answer", ""))
    char_count = len(answer)

    if char_count < 50:
        return {"key": "length_ok", "score": 0.0,
                "comment": f"太短({char_count} 字)"}
    elif char_count <= 400:
        return {"key": "length_ok", "score": 1.0,
                "comment": f"理想長度({char_count} 字)"}
    elif char_count <= 800:
        return {"key": "length_ok", "score": 0.7,
                "comment": f"可接受({char_count} 字)"}
    else:
        return {"key": "length_ok", "score": 0.3,
                "comment": f"太長({char_count} 字)"}


# 4d. 規則型:技術關鍵詞覆蓋率
def eval_keywords(inputs: dict, outputs: dict,
                  reference_outputs: dict | None = None, **kwargs) -> dict:

    if not reference_outputs:
        return {"key": "keyword_coverage", "score": 0.5, "comment": "無參考答案"}

    ref = str(reference_outputs.get("answer", ""))
    out = str(outputs.get("answer", ""))
    # \w{4,} 已保證長度 ≥ 4,不需要額外的 len() 檢查
    keywords = set(re.findall(r'[A-Za-z_]\w{3,}', ref))

    if not keywords:
        return {"key": "keyword_coverage", "score": 1.0, "comment": "N/A"}

    found = {kw for kw in keywords if kw.lower() in out.lower()}
    coverage = len(found) / len(keywords)
    missing = keywords - found
    comment = f"{len(found)}/{len(keywords)} 關鍵詞命中"

    if missing and len(missing) <= 5:
        comment += f",缺少:{', '.join(missing)}"
    elif missing:
        comment += f",缺少 {len(missing)} 個關鍵詞"

    return {"key": "keyword_coverage", "score": round(coverage, 2), "comment": comment}

all_evaluators = [eval_correctness, eval_conciseness, eval_length, eval_keywords]
print(f"✅ Step 4:已定義 {len(all_evaluators)} 個 Evaluator")

# ============================================================
# Step 5:執行 Experiment(兩組)
# ============================================================

print("\n🚀 Step 5:開始執行 Experiment...")
print("-" * 40)
print("⏳ 執行基礎版 Agent...")

results_basic = ls_client.evaluate(
    agent_basic,
    data=DATASET_NAME,
    evaluators=all_evaluators,
    experiment_prefix="Basic-Agent",
    description="基礎版 Agent:最小化 System Prompt",
)

print("✅ 基礎版完成")
print("⏳ 執行專家版 Agent...")

results_expert = ls_client.evaluate(
    agent_expert,
    data=DATASET_NAME,
    evaluators=all_evaluators,
    experiment_prefix="Expert-Agent",
    description="專家版 Agent:精心設計的 System Prompt",
)

print("✅ 專家版完成")

# ============================================================
# Step 6:在程式中摘要結果
# ============================================================

print("\n" + "=" * 60)
print("📊 評估結果摘要")
print("=" * 60)

def summarize_results(results, label: str):
    """統計評估結果"""
    scores = {}

    for result in results:
        # result 是 dict,用 .get() 而非 hasattr / 屬性存取
        if isinstance(result, dict):
            eval_data = result.get("evaluation_results") or {}
        else:
            eval_data = getattr(result, "evaluation_results", None) or {}

        # evaluation_results 本身可能是 dict 或物件
        if isinstance(eval_data, dict):
            result_list = eval_data.get("results", [])
        else:
            result_list = getattr(eval_data, "results", [])

        for eval_result in result_list:
            # eval_result 也可能是 dict 或物件,統一處理
            if isinstance(eval_result, dict):
                key = eval_result.get("key", "unknown")
                score = eval_result.get("score")
            else:
                key = getattr(eval_result, "key", "unknown")
                score = getattr(eval_result, "score", None)

            if score is None:
                continue

            if key not in scores:
                scores[key] = []

            if isinstance(score, bool):
                scores[key].append(1.0 if score else 0.0)
            elif isinstance(score, (int, float)):
                scores[key].append(float(score))

    print(f"\n🤖 {label}:")

    if not scores:
        print("   ⚠️  無法取得評分資料,請確認 Evaluator 是否正常執行")
        return

    for key, vals in scores.items():
        avg = sum(vals) / len(vals) if vals else 0
        print(f"   {key:25s}: 平均 {avg:.2f}  "
              f"(min={min(vals):.2f}, max={max(vals):.2f}, n={len(vals)})")

summarize_results(results_basic, "基礎版 Agent")
summarize_results(results_expert, "專家版 Agent")

print("\n" + "=" * 60)
print("🎯 後續步驟:")
print("   1. 前往 LangSmith Dashboard 查看詳細的 Experiment 比較")
print("   2. 對分數低的案例進行 Root Cause 分析")
print("   3. 建立 Pairwise Annotation Queue 讓團隊成員做人工評審")
print("   4. 根據分析結果迭代 System Prompt 或 RAG 策略")
print("=" * 60)