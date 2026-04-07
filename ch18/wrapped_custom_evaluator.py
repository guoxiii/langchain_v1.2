# wrapped_custom_evaluator.py

from dotenv import load_dotenv
load_dotenv()

from openevals.utils import _run_evaluator

# ============================================================
# 使用 _run_evaluator 包裝的自定義 Evaluator
# ============================================================

def create_citation_checker():
    """建立一個檢查 RAG 回答是否包含引用來源的評估器"""

    def scorer(
        *,
        inputs: str | None = None,
        outputs: str | None = None,
        reference_outputs: str | None = None,
        **kwargs,
    ) -> tuple[bool, str]:
        answer = str(outputs) if outputs else ""
        citation_patterns = ["來源", "參考", "引用", "出處", "[ref", "source:", "根據"]
        has_citation = any(pattern in answer for pattern in citation_patterns)

        if has_citation:
            return True, "回答中包含引用來源標記"
        else:
            return False, "回答中缺少引用來源，RAG 系統應該標明資訊出處"

    # 外層包一個 callable，呼叫時才執行 _run_evaluator
    def evaluator(
        *,
        inputs: str | None = None,
        outputs: str | None = None,
        reference_outputs: str | None = None,
        **kwargs,
    ):
        # _run_evaluator 在這裡才被呼叫，同時觸發 LangSmith tracing
        result = _run_evaluator(
            run_name="citation_checker",
            scorer=scorer,
            feedback_key="has_citation",
            inputs=inputs,
            outputs=outputs,
            reference_outputs=reference_outputs,
            **kwargs,
        )
        # _run_evaluator 可能回傳 dict（單筆）或 list（多筆），統一取第一筆
        if isinstance(result, list):
            return result[0] if result else {}
        return result

    return evaluator


# 建立評估器實例
citation_evaluator = create_citation_checker()

# 測試
result = citation_evaluator(
    inputs="LangChain v1 有哪些變化？",
    outputs="根據官方文件，LangChain v1 的主要變化包括：LCEL 已被淘汰、"
            "create_agent 取代 create_react_agent、新增 Middleware 系統。"
            "（來源：LangChain v1 Release Notes）",
)

print(f"引用檢查：{result['score']}，{result['comment']}")