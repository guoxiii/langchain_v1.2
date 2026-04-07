"""
商品推薦 Agent 模組
結合 Vector Store 與 Knowledge Graph 進行智能推薦
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from src.product_knowledge import get_vector_store
from src.product_graph import ProductGraphBuilder

# ============================================================
# 定義 Structured Output Schema
# ============================================================

class ProductRecommendation(BaseModel):
    """單一商品推薦結果"""
    product_id: str = Field(description="商品編號")
    product_name: str = Field(description="商品名稱")
    price: int = Field(description="價格（TWD）")
    reason: str = Field(description="推薦理由，需要具體說明為什麼這個商品適合使用者")

    confidence: float = Field(
        description="推薦信心分數（0.0 到 1.0）",
        ge=0.0,
        le=1.0,
    )

class RecommendationResponse(BaseModel):
    """推薦回應的完整結構"""
    greeting: str = Field(description="親切的問候語")

    recommendations: list[ProductRecommendation] = Field(
        description="推薦的商品列表（最多 5 項）",
        max_length=5,
    )

    skincare_tip: str = Field(description="一則額外的保養小建議")

    follow_up_question: str = Field(
        description="引導使用者進一步互動的問題"
    )

# ============================================================
# 定義工具
# ============================================================

# 初始化共用資源
_vector_store = None
_graph_builder = None

def _get_vector_store():
    global _vector_store

    if _vector_store is None:
        _vector_store = get_vector_store()

    return _vector_store

def _get_graph_builder():
    global _graph_builder

    if _graph_builder is None:
        _graph_builder = ProductGraphBuilder(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
        )

    return _graph_builder

@tool
def search_products_by_description(query: str) -> str:
    """
    根據使用者的自然語言描述搜尋相關商品。
    適合用於：使用者描述他們的需求、膚質、或想要的功效時。    

    Args:
        query: 使用者的搜尋描述，例如「我想要控油的洗面乳」或「適合敏感肌的保濕產品」    

    Returns:
        搜尋結果的 JSON 字串，包含最相關的商品資訊
    """
    vs = _get_vector_store()
    results = vs.similarity_search_with_relevance_scores(query, k=5)
    output = []

    for doc, score in results:
        output.append({
            "product_id": doc.metadata["product_id"],
            "name": doc.metadata["name"],
            "category": doc.metadata["category"],
            "price": doc.metadata["price"],
            "rating": doc.metadata["rating"],
            "stock": doc.metadata["stock"],
            "relevance_score": round(score, 3),
            "description_snippet": doc.page_content[:200],
        })

    return json.dumps(output, ensure_ascii=False, indent=2)

@tool
def get_related_products(product_id: str) -> str:
    """
    查詢與指定商品相關的其他商品（透過知識圖譜）。
    包括：推薦搭配、共同成分、相同膚質適用等多種關聯。
   
    Args:
        product_id: 商品編號，例如 "P001"   

    Returns:
        相關商品列表的 JSON 字串
    """

    gb = _get_graph_builder()
    related = gb.query_related_products(product_id)
    return json.dumps(related, ensure_ascii=False, indent=2)

@tool
def get_skincare_routine(skin_type: str) -> str:
    """
    根據使用者的膚質，推薦完整的保養流程。
    會按照正確的使用順序排列：卸妝 → 潔面 → 化妝水 → 精華液 → 乳霜 → 防曬。    

    Args:
        skin_type: 膚質類型，可選值："油性"、"混合性"、"乾性"、"敏感肌"、"所有膚質"、"男性膚質"    

    Returns:
        保養流程的 JSON 字串
    """
    gb = _get_graph_builder()
    routine = gb.query_skincare_routine(skin_type)
    return json.dumps(routine, ensure_ascii=False, indent=2)

@tool
def get_products_by_skin_type(skin_type: str) -> str:
    """
    根據膚質查詢所有適合的商品，按評分排序。    

    Args:
        skin_type: 膚質類型    

    Returns:
        適合該膚質的商品列表
    """
    gb = _get_graph_builder()
    products = gb.query_by_skin_type(skin_type)
    return json.dumps(products, ensure_ascii=False, indent=2)

@tool
def check_product_stock(product_id: str) -> str:
    """
    查詢指定商品的庫存狀態。    

    Args:
        product_id: 商品編號    

    Returns:
        庫存資訊
    """
    vs = _get_vector_store()
    results = vs.similarity_search(
        f"商品編號 {product_id}",
        k=1,
        filter={"product_id": product_id},
    )

    if results:
        meta = results[0].metadata
        stock = meta.get("stock", 0)
        status = "充足" if stock > 50 else "偏低" if stock > 10 else "即將售罄"

        return json.dumps({
            "product_id": product_id,
            "name": meta["name"],
            "stock": stock,
            "status": status,
        }, ensure_ascii=False)

    return json.dumps({"error": f"找不到商品 {product_id}"}, ensure_ascii=False)


# ============================================================
# 建立推薦 Agent
# ============================================================
def create_recommendation_agent(checkpointer=None):
    """建立商品推薦 Agent

    Args:
        checkpointer: 可選的 Checkpointer，傳入後即支援多輪對話記憶。
                      例如 MemorySaver()（開發測試用）或
                      PostgresSaver / SqliteSaver（正式環境用）。
    """

    tools = [
        search_products_by_description,
        get_related_products,
        get_skincare_routine,
        get_products_by_skin_type,
        check_product_stock,
    ]

    system_prompt = """你是一位專業且親切的電商美妝保養品顧問 AI。你的名字叫「小美」。

你的職責：
1. 根據顧客的膚質、需求和偏好，推薦最適合的商品
2. 解釋商品的成分和功效，用淺顯易懂的方式
3. 推薦完整的保養流程，而不只是單一產品
4. 如果商品庫存不足，主動提醒顧客

你的風格：
- 親切友善，像是跟朋友聊天一樣
- 專業但不說教，用生活化的比喻解釋成分功效
- 主動詢問顧客的膚質和需求，而非只被動回答
- 適時推薦相關商品，但不要過度推銷

重要規則：
- 一定要先用工具搜尋商品資訊，不要憑空推薦
- 推薦時要說明具體的推薦理由
- 如果顧客的問題超出商品範圍（如醫療問題），請禮貌建議諮詢專業醫師
- 回覆時保持簡潔，避免過長的段落
"""

    agent = create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=tools,
        system_prompt=system_prompt,
        response_format=RecommendationResponse,
        checkpointer=checkpointer,
    )

    return agent

# ============================================================
# 格式化輸出工具
# ============================================================

def _print_structured_response(data: dict) -> None:
    """將 RecommendationResponse 結構化資料格式化印出"""

    print(f"🤖 小美：{data.get('greeting', '')}\n")

    recommendations = data.get("recommendations", [])
    for i, rec in enumerate(recommendations, 1):
        name = rec.get("product_name", "未知商品")
        pid = rec.get("product_id", "")
        price = rec.get("price", "?")
        confidence = rec.get("confidence", 0)
        reason = rec.get("reason", "")

        print(f"  {i}. {name} ({pid})  NT${price}  "
              f"[信心 {confidence:.0%}]")
        print(f"     → {reason}")

    tip = data.get("skincare_tip", "")
    if tip:
        print(f"\n  💡 保養小建議：{tip}")

    follow_up = data.get("follow_up_question", "")
    if follow_up:
        print(f"\n  ❓ {follow_up}")


# ============================================================
# 測試推薦 Agent
# ============================================================

if __name__ == "__main__":
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

    # 建立自訂序列化器，將 RecommendationResponse 加入白名單
    # 這樣 MemorySaver 在多輪對話中反序列化 checkpoint 時
    # 就能正確還原自訂的 Pydantic 類別，不再發出警告
    serde = JsonPlusSerializer(
        allowed_msgpack_modules=[("__main__", "RecommendationResponse")]
    )

    # 透過同一個函式建立，確保 system_prompt、response_format 都一致
    agent = create_recommendation_agent(
        checkpointer=MemorySaver(serde=serde)
    )
    config = {"configurable": {"thread_id": "customer-001"}}

    test_queries = [
        "我是油性肌膚，最近T區很容易出油，有什麼推薦的？",
        "幫我推薦一套完整的保養流程，我是混合性肌膚",
        "P001 這個洗面乳還有庫存嗎？有沒有什麼可以搭配的？",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"👤 顧客：{query}")
        print(f"{'='*60}")

        result = agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config=config,
        )

        # ── 取得結構化回應 ──
        # 使用 response_format 時，結構化結果存放在
        # result["structured_response"]，型別為 RecommendationResponse
        structured = result.get("structured_response")

        if structured is not None:
            # structured 是 Pydantic Model，用 model_dump() 轉為 dict
            data = (
                structured.model_dump()
                if hasattr(structured, "model_dump")
                else structured  # 已經是 dict 的備援
            )
            _print_structured_response(data)
        else:
            # 備援：若 structured_response 不存在，印出最後一則訊息
            last_message = result["messages"][-1]
            print(f"🤖 小美：{last_message.content}")