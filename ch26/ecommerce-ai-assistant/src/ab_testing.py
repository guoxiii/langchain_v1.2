# src/ab_testing.py

"""
A/B 測試模組
使用 LangSmith 比較不同推薦策略的效能
"""

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from langsmith.evaluation import evaluate
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import json
from src.recommendation import search_products_by_description, get_related_products, get_skincare_routine

# ============================================================
# 策略 A：基於語義相似度推薦（偏向「你搜什麼給你什麼」）
# ============================================================

def strategy_a_agent():
    """策略 A：純向量搜尋推薦"""
    return create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[search_products_by_description],
        system_prompt="""你是保養品推薦助理。

推薦規則：
- 嚴格根據使用者的描述搜尋最相關的商品
- 只推薦語義搜尋排名前 3 的商品
- 不要額外推薦使用者沒提到的品類
""",
    )

# ============================================================
# 策略 B：GraphRAG 混合推薦（偏向「延伸推薦」）
# ============================================================

def strategy_b_agent():
    """策略 B：向量搜尋 + 知識圖譜推薦"""
    return create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=[
            search_products_by_description,
            get_related_products,
            get_skincare_routine,
        ],
        system_prompt="""你是保養品推薦助理。

推薦規則：
- 先根據使用者描述搜尋相關商品
- 再查詢知識圖譜，找出關聯商品和保養流程
- 主動推薦完整的保養方案，而非只回答使用者的直接問題
- 解釋商品之間的搭配關係
""",
    )


# ============================================================
# 建立測試資料集
# ============================================================

def create_test_dataset():
    """建立推薦品質測試資料集"""
    client = Client()
    dataset_name = "ecommerce-recommendation-test"

    # 檢查資料集是否已存在
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"✅ 資料集 '{dataset_name}' 已存在，跳過建立")
        return dataset
    except Exception:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="電商推薦策略 A/B 測試資料集",
    )

    # 測試案例：每個案例包含顧客查詢和理想回應的特徵
    test_cases = [
        {
            "input": "我是油性肌膚，最近出油很嚴重",
            "expected_categories": ["潔面", "化妝水"],
            "expected_min_products": 2,
            "customer_need": "控油",
        },
        {
            "input": "有沒有防曬推薦？要清爽不黏膩的",
            "expected_categories": ["防曬"],
            "expected_min_products": 1,
            "customer_need": "防曬",
        },
        {
            "input": "想要一整套的保養流程，混合性肌膚",
            "expected_categories": ["潔面", "化妝水", "精華液", "防曬"],
            "expected_min_products": 3,
            "customer_need": "完整保養",
        },
        {
            "input": "臉上有痘印想淡化",
            "expected_categories": ["精華液"],
            "expected_min_products": 1,
            "customer_need": "美白淡斑",
        },
        {
            "input": "男生用的保養品有什麼？",
            "expected_categories": ["乳霜"],
            "expected_min_products": 1,
            "customer_need": "男士保養",
        },
    ]

    for case in test_cases:
        client.create_example(
            inputs={"query": case["input"]},
            outputs={
                "expected_categories": case["expected_categories"],
                "expected_min_products": case["expected_min_products"],
                "customer_need": case["customer_need"],
            },
            dataset_id=dataset.id,
        )

    print(f"✅ 已建立測試資料集，共 {len(test_cases)} 個測試案例")
    return dataset

# ============================================================
# 定義評估器
# ============================================================

def recommendation_relevance_evaluator(run, example):
    """
    評估推薦結果的相關性。
    使用 LLM-as-Judge 的方式，讓另一個 LLM 評分推薦品質。
    """
    model = init_chat_model("anthropic:claude-sonnet-4-6")
    query = example.inputs["query"]
    response = run.outputs.get("output", "")
    expected_need = example.outputs["customer_need"]
    judge_prompt = f"""你是一位電商推薦品質評審。請根據以下標準評估推薦結果：

顧客查詢：{query}
顧客核心需求：{expected_need}
AI 推薦回覆：{response}

評分標準（每項 1-5 分）：
1. 相關性：推薦的商品是否符合顧客的需求？
2. 完整性：是否推薦了足夠的商品？是否包含搭配建議？
3. 解釋性：是否清楚說明了推薦理由？
4. 實用性：推薦是否有助於顧客做出購買決定？

請只回覆一個 JSON 物件，格式如下：
{{"relevance": 分數, "completeness": 分數, "explanation": 分數, "usefulness": 分數, "total": 總分, "comment": "一句話評語"}}
"""

    result = model.invoke(judge_prompt)

    try:
        # 嘗試解析 JSON
        content = result.content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]

        scores = json.loads(content)

        return {
            "key": "recommendation_quality",
            "score": scores.get("total", 0) / 20,  # 正規化到 0-1
            "comment": scores.get("comment", ""),
        }

    except (json.JSONDecodeError, KeyError):
        return {
            "key": "recommendation_quality",
            "score": 0.5,
            "comment": "評估解析失敗",
        }

# ============================================================
# 執行 A/B 測試
# ============================================================

def run_ab_test():
    """執行 A/B 測試"""
    dataset = create_test_dataset()

    # 定義目標函式 — 策略 A
    def target_a(inputs: dict) -> dict:
        agent = strategy_a_agent()
        result = agent.invoke({
            "messages": [{"role": "user", "content": inputs["query"]}]
        })

        return {"output": result["messages"][-1].content}

    # 定義目標函式 — 策略 B
    def target_b(inputs: dict) -> dict:
        agent = strategy_b_agent()
        result = agent.invoke({
            "messages": [{"role": "user", "content": inputs["query"]}]
        })

        return {"output": result["messages"][-1].content}

    # 執行策略 A 的評估
    print("\n📊 執行策略 A 評估（純向量搜尋）...")

    results_a = evaluate(
        target_a,
        data=dataset.name,
        evaluators=[recommendation_relevance_evaluator],
        experiment_prefix="strategy-a-vector-only",
    )

    # 執行策略 B 的評估
    print("\n📊 執行策略 B 評估（GraphRAG 混合推薦）...")

    results_b = evaluate(
        target_b,
        data=dataset.name,
        evaluators=[recommendation_relevance_evaluator],
        experiment_prefix="strategy-b-graphrag",
    )

    # ── 彙整結果 ──
    print("\n" + "=" * 60)
    print("📈 A/B 測試結果摘要")
    print("=" * 60)

    df_a = results_a.to_pandas()
    df_b = results_b.to_pandas()

    score_a = df_a["feedback.recommendation_quality"].mean()
    score_b = df_b["feedback.recommendation_quality"].mean()

    print(f"策略 A（純向量搜尋）：")
    print(f"  平均推薦品質分數：{score_a:.4f}")
    print(f"\n策略 B（GraphRAG 混合）：")
    print(f"  平均推薦品質分數：{score_b:.4f}")

    if score_b > score_a:
        print(f"\n🏆 策略 B 勝出，領先 {score_b - score_a:.4f} 分")
    elif score_a > score_b:
        print(f"\n🏆 策略 A 勝出，領先 {score_a - score_b:.4f} 分")
    else:
        print(f"\n🤝 兩者持平")

    print(f"\n🔗 詳細結果請前往 LangSmith Dashboard 查看")
    print(f"   https://smith.langchain.com")

if __name__ == "__main__":
    run_ab_test()