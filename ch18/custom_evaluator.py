# custom_evaluator.py

from dotenv import load_dotenv
load_dotenv()

# ============================================================
# 自定義 Evaluator 範例一：回答長度檢查
# ============================================================

def answer_length_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict | None = None,
) -> dict:
    """檢查回答是否在合理的長度範圍內"""
    answer = outputs.get("answer", "")
    length = len(answer)

    if length < 20:
        score = 0.0
        comment = f"回答太短（{length} 字），可能資訊不足"
    elif length < 50:
        score = 0.5
        comment = f"回答偏短（{length} 字），可能需要更多細節"
    elif length < 500:
        score = 1.0
        comment = f"回答長度適中（{length} 字）"
    elif length < 1000:
        score = 0.7
        comment = f"回答偏長（{length} 字），可以更簡潔"
    else:
        score = 0.3
        comment = f"回答過長（{length} 字），需要精簡"

    return {
        "key": "answer_length",
        "score": score,
        "comment": comment,
    }


# ============================================================
# 自定義 Evaluator 範例二：關鍵詞覆蓋率
# ============================================================

def keyword_coverage_evaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict | None = None,
) -> dict:
    """檢查回答是否包含參考答案中的關鍵技術名詞"""
    if reference_outputs is None:
        return {"key": "keyword_coverage", "score": 0.0, "comment": "無參考答案可比對"}

    reference = reference_outputs.get("answer", "")
    answer = outputs.get("answer", "")

    # 提取技術關鍵詞（簡化版：取英文單字和特定模式）
    import re
    keywords = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]+', reference))

    # 過濾掉太短的（可能是 a, is, the 等）
    keywords = {kw for kw in keywords if len(kw) > 3}

    if not keywords:
        return {"key": "keyword_coverage", "score": 1.0, "comment": "參考答案中無技術關鍵詞"}

    found = {kw for kw in keywords if kw.lower() in answer.lower()}
    coverage = len(found) / len(keywords)
    missing = keywords - found
    comment = f"覆蓋率 {coverage:.0%} ({len(found)}/{len(keywords)} 個關鍵詞)"

    if missing:
        comment += f"。缺少：{', '.join(list(missing)[:5])}"

    return {
        "key": "keyword_coverage",
        "score": round(coverage, 2),
        "comment": comment,
    }

# ============================================================
# 測試自定義 Evaluator
# ============================================================

test_inputs = {"question": "什麼是 Middleware？"}

test_outputs = {
    "answer": "Middleware 是 LangChain v1 的核心機制，提供 before_model、"
              "after_model、wrap_tool_call 等 Hook 來控制 Agent 行為。"
}

test_reference = {
    "answer": "Middleware 是 LangChain v1 的機制，提供 before_agent、before_model、"
              "after_model、after_agent、wrap_model_call、wrap_tool_call 六大 Hook。"
}

result1 = answer_length_evaluator(test_inputs, test_outputs, test_reference)
result2 = keyword_coverage_evaluator(test_inputs, test_outputs, test_reference)

print(f"📏 長度評估：score={result1['score']}, {result1['comment']}")
print(f"🔑 關鍵詞覆蓋：score={result2['score']}, {result2['comment']}")
